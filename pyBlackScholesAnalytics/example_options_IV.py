import numpy as np
import pandas as pd
import warnings

from market.market import MarketEnvironment
from options.options import PlainVanillaOption, DigitalOption

warnings.filterwarnings("ignore")

def option_factory(mkt_env, plain_or_digital, option_type):

    option_dispatcher = {
            "plain_vanilla": {"call": PlainVanillaOption(mkt_env),
                              "put":  PlainVanillaOption(mkt_env, option_type="put")
                             },
            "digital": {"call": DigitalOption(mkt_env),
                        "put":  DigitalOption(mkt_env, option_type="put")
                       }
    }
    
    return option_dispatcher[plain_or_digital][option_type]

def main():

    #
    # Black-Scholes implied volatility calculation with user-defined 'sigma' 
    # parameter surface, used to evaluate the quality of the implied volatility 
    # calculation.
    #
    
    # output format: pd.DataFrame    
    np_output = False 
    
    # default market environment
    market_env = MarketEnvironment()
    print(market_env)
    
    # define option style and type
    opt_style = "plain_vanilla" # "digital"
    opt_type = "call" # "call" # "put"   
    option = option_factory(market_env, opt_style, opt_type)
    print(option)
    
    # K
    K_vector = [50, 75, 100, 125, 150]

    # tau: a date-range of 5 valuation dates between t and T-10d
    n = 6
    valuation_date = option.get_t()
    expiration_date = option.get_T()
    t_vector = pd.date_range(start=valuation_date, 
                             end=expiration_date-pd.Timedelta(days=25), 
                             periods=n)    
    
    # sigma (qualitatively reproducing the smile)
    k, tau = np.meshgrid(K_vector, option.time_to_maturity(t=t_vector))
    sigma_grid_K = 0.01 + ((k - 100)**2)/(100*k*tau)
    
    # pricing parameters
    param_dict = {"S": 100,
                  "K": K_vector,
                  "t": t_vector,
                  "sigma": sigma_grid_K,
                  "r": 0.01,
                  "np_output": np_output}

    print("Parameters:")
    print("S: {}".format(param_dict["S"]))
    print("K: {}".format(param_dict["K"]))
    print("t: {}".format(param_dict["t"]))
    print("sigma: \n{}".format(param_dict["sigma"]))
    print("r: {}\n".format(param_dict["r"]))
    
    # expected implied volatility: is the 'sigma' parameter with which the 
    # target price has been generated
    expected_IV = pd.DataFrame(data=param_dict["sigma"],
                               columns=K_vector,
                               index=t_vector)
    print("\nExpected Kxt Implied volatiltiy Surface: \n", expected_IV)
    
    #
    # Without target_price in input: param_dict['sigma'] parameter is 
    # used to construct target price, used in minimization
    #
    
    print("\n--- WITHOUT target_price in input ---\n")

    # newton method
    newton_IV = option.implied_volatility(**param_dict)
    RMSE_newton = np.sqrt(np.nanmean((newton_IV - expected_IV)**2))
    RMSRE_newton = np.sqrt(np.nanmean(((newton_IV - expected_IV)/expected_IV)**2))
    print("\nImplied Volatility - Newton method - Metrics (NaN excluded): RMSE={:.1E}, RMSRE={:.1E}:\n"\
          .format(RMSE_newton, RMSRE_newton), newton_IV)
    
    # Least=Squares method
    param_dict["minimization_method"] = "Least-Squares"
    ls_IV = option.implied_volatility(**param_dict)
    RMSE_ls = np.sqrt(np.nanmean((ls_IV - expected_IV)**2))
    RMSRE_ls = np.sqrt(np.nanmean(((ls_IV - expected_IV)/expected_IV)**2))

    print("\nImplied Volatility - Newton method - Metrics (NaN excluded): RMSE={:.1E}, RMSRE={:.1E}:\n"\
          .format(RMSE_ls, RMSRE_ls), ls_IV)

    #
    # With target_price in input: target_price, but no param_dict['sigma'],
    # is used in minimization.
    #
    
    print("\n--- WITH target_price in input ---\n")

    # compute target price
    target_price = option.price(**param_dict)
    print("\nTarget Price in input: \n", target_price)

    # Add target_price to parameters dictionary:
    param_dict['target_price'] = target_price

    # Remove from implied volatility parameters in input the 'sigma' parameter
    # it's not necessary, but this way for sure the .implied_volatility() method
    # is agnostic of the expected implied volatility
    del param_dict['sigma']
        
    # newton method
    newton_IV = option.implied_volatility(**param_dict)
    RMSE_newton = np.sqrt(np.nanmean((newton_IV - expected_IV)**2))
    RMSRE_newton = np.sqrt(np.nanmean(((newton_IV - expected_IV)/expected_IV)**2))
    print("\nImplied Volatility - Newton method - Metrics (NaN excluded): RMSE={:.1E}, RMSRE={:.1E}:\n"\
          .format(RMSE_newton, RMSRE_newton), newton_IV)
    
    # Least=Squares method
    param_dict["minimization_method"] = "Least-Squares"
    ls_IV = option.implied_volatility(**param_dict)
    RMSE_ls = np.sqrt(np.nanmean((ls_IV - expected_IV)**2))
    RMSRE_ls = np.sqrt(np.nanmean(((ls_IV - expected_IV)/expected_IV)**2))

    print("\nImplied Volatility - Newton method - Metrics (NaN excluded): RMSE={:.1E}, RMSRE={:.1E}:\n"\
          .format(RMSE_ls, RMSRE_ls), ls_IV)

#----------------------------- usage example ---------------------------------#
if __name__ == "__main__":
    
    main()    
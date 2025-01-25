CREATE TABLE IF not EXISTS stock_data (
    stock_symbol SYMBOL,  
    topic STRING,  
    signal STRING,    
    local_time TIMESTAMP, 
    open DOUBLE,          
    close DOUBLE,        
    high DOUBLE,          
    low DOUBLE,           
    volume LONG,          
    SMA_5 DOUBLE,         
    EMA_10 DOUBLE,        
    delta DOUBLE,
    gain DOUBLE,
    loss DOUBLE,
    avg_gain_10 DOUBLE,
    avg_loss_10 DOUBLE,
    rs DOUBLE,
    RSI_10 DOUBLE
)
TIMESTAMP(local_time)
PARTITION BY DAY;
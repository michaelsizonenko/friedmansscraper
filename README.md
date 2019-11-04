Written for Python 2.7.9

check python is in the System Path variable (check by typing 'echo %PATH%' and press enter) 

config.json meaning : 

{
  "input_file": "C:/some_dir/test2.csv", --- absolute path to the input csv file (use slash only / instead of backslash \ )
  "output_file": "C:/some_dir/result.csv" --- absolute path to the output csv file
  "depth": 5,                --- depth of parsing
  "name_index": 1,           --- column in csv contains person name (number order starts from 0)
  "start_from": 0,           --- start row. file will be processed from this row number
  "process_until": 3001,     --- the last row to process
  "continue_processing": false  --- false if you want to remove old results and create new result.csv; 
                                    true if you want continue writing to the same file
}


other configuration parameters:

spiders/settings.py contains:

ROBOTSTXT_OBEY = False  -- True if spider need to ask robots.txt file
RETRY_ENABLED = False   -- True if you want to retry request URL failed to load
DOWNLOAD_TIMEOUT = 30   -- download timeout for a single URL
RETRY_TIMES = 1         -- retry numbers if failed to download URL


All params are explained above and stored in config.json or settings.py

To run spider:

python main.py
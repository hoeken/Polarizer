# Polarizer
Scripts for generating and manipulating sailing polars.  Currently works with B&G NMEA0183 over IP.

Data Collection:

You can assign an arbitrary name to your particular sail configuration and it will log all the raw data to a file.

python log-nmea0183-over-ip.py -c 'twin bow spin'
python log-nmea0183-over-ip.py -c 'bowsprit spin'
python log-nmea0183-over-ip.py -c 'screacher and full main'
python log-nmea0183-over-ip.py -c 'jib and full main'
python log-nmea0183-over-ip.py -c 'jib and first reef'
python log-nmea0183-over-ip.py -c 'jib and second reef'

Polar Generation:

Afterwards, you can generate polars for each individual sail configuration and then combine them into a single 'best sailset' file.

python generate-polars.py -d 'data/screacher and full main'
python generate-polars.py -d 'data/jib and full main'
python generate-polars.py -d 'data/jib and first reef'
python generate-polars.py --twa_min=110 -d 'data/twin bow spin'
python generate-polars.py --twa_min=110 -d 'data/bowsprit spin'
python combine-polars.py -a 'screacher and full main' -b 'jib and full main' -c 'jib and first reef' -d 'twin bow spin' -e 'bowsprit spin'

Utility:

You can also manually choose what sail data to use for a particular TWA/TWS with the use of a legend file:

python legend-polars.py -l polars/combined-polars-legend.csv -s polars/combined-polars-sailset.csv
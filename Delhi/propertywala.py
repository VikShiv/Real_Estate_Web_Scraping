# -*- coding: utf-8 -*-
import scrapy
from ..items import PropertywaladelhisaleItem
from scrapy.selector import Selector
from scrapy.http import Request
import re
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
# import docx


class PropertywalasalenewdelhiSpider(scrapy.Spider):
    name = "propertywalaDelhi"
    allowed_domains = ["propertywala.com"]
    start_urls = [
        'https://www.propertywala.com/properties/type-residential/for-sale/location-new_delhi?orderby=date',
        'https://www.propertywala.com/properties/type-residential/for-sale/location-greater_noida_uttar_pradesh?orderby=date/',
        'https://www.propertywala.com/properties/type-residential/for-sale/location-faridabad_haryana?orderby=date/',
        'https://www.propertywala.com/properties/type-residential/for-sale/location-ghaziabad_uttar_pradesh?orderby=date/',
        'https://www.propertywala.com/properties/type-residential/for-sale/location-gurgaon_haryana?orderby=date/',
        'https://www.propertywala.com/properties/type-residential/for-sale/location-noida_uttar_pradesh?orderby=date/',
        'https://www.propertywala.com/properties/type-residential/for-rent/location-new_delhi?orderby=date',
        'https://www.propertywala.com/properties/type-residential/for-rent/location-noida_uttar_pradesh?orderby=date',
        'https://www.propertywala.com/properties/type-residential/for-rent/location-greater_noida_uttar_pradesh?orderby=date',
        'https://www.propertywala.com/properties/type-residential/for-rent/location-gurgaon_haryana?orderby=date',
        'https://www.propertywala.com/properties/type-residential/for-rent/location-faridabad_haryana?orderby=date',
        'https://www.propertywala.com/properties/type-residential/for-rent/location-ghaziabad_uttar_pradesh?orderby=date',
    ]
    custom_settings = {
        'DEPTH_LIMIT': 10000,
        'DOWNLOAD_DELAY': 5.0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
    }
    item = PropertywaladelhisaleItem()
    # doc = docx.Document()

    def parse(self, response):
        try:
            record = Selector(response)
            data = record.xpath('//li[@class="posted"]')

            txn = city = ''
            cityurl = str(response.url)

            if 'faridabad' in cityurl:
                city = 'Faridabad'
            elif 'ghaziabad' in cityurl:
                city = 'Ghaziabad'
            elif 'new_delhi' in cityurl:
                city = 'New Delhi'
            elif 'noida' in cityurl:
                if 'greater_noida' in cityurl:
                    city = 'Greater Noida'
                else:
                    city = 'Noida'
            elif 'gurgaon' in cityurl:
                city = 'Gurgaon'

            if 'rent' in cityurl:
                txn = 'Rent'
            elif 'sale' in cityurl:
                txn = 'Sale'

            for i in data:
                ids = i.xpath('text()').extract_first().strip().encode('ascii', 'ignore').decode('ascii').replace('ID: ', '').replace('  Posted:', '')
                checkprop = response.xpath('//*[@id="' + ids + '"]/header/h4/a/text()').extract_first().strip()
                if 'Land' in checkprop:
                    continue
                try:
                    d = response.xpath("//*[contains(@id,'" + ids + "')]/div/ul/li[3]/span/@title").extract_first()
                    name_lister = response.xpath("//*[contains(@id,'" + ids + "')]/div/ul/li[3]/span/text()").extract_first()
                    if d is None:
                        d = response.xpath("//*[contains(@id,'" + ids + "')]/div/ul/li[3]/a/@title").extract_first()
                        name_lister = response.xpath("//*[contains(@id,'" + ids + "')]/div/ul/li[3]/a/text()").extract_first()

                    if 'wner' in d.lower():
                        d = 'Owner'
                    elif 'uilder' in d.lower():
                        d = 'Builder'
                    elif 'roker' in d.lower():
                        d = 'Agent'
                    else:
                        d = 'Propertywala User'

                    url = 'https://www.propertywala.com/' + i.xpath('text()').extract_first().strip().encode('ascii', 'ignore').decode('ascii').replace('ID: ', '').replace('  Posted:', '')
                    request = Request(url, callback=self.parse1, dont_filter=True)
                    request.meta['agent'] = d
                    request.meta['name'] = name_lister
                    request.meta['data_id'] = ids
                    request.meta['city'] = city
                    request.meta['txn'] = txn
                    yield request
                except Exception as e:
                    print(e)
            nextPage = response.xpath('*//a[contains(@title,"Next Page")]/@href').extract_first(default='None')
            if nextPage is not 'None':
                url = 'https://www.propertywala.com' + nextPage
                yield Request(url, callback=self.parse, dont_filter=True)
        except Exception as e:
            print(e)

    def parse1(self, response):
        self.item['Selling_price'] = '0'
        self.item['Possession'] = '0'
        self.item['Status'] = 'None'
        self.item['carpet_area'] = '0'
        self.item['management_by_landlord'] = 'None'
        self.item['areacode'] = '0'
        self.item['mobile_lister'] = 'None'
        self.item['google_place_id'] = '0'
        self.item['Launch_date'] = '0'
        self.item['age'] = '0'
        self.item['address'] = 'None'
        self.item['price_on_req'] = 'FALSE'
        self.item['Details'] = 'None'
        self.item['Monthly_Rent'] = '0'
        self.item['sublocality'] = 'None'
        self.item['price_per_sqft'] = '0'
        self.item['platform'] = 'Propertywala'
        self.item['Building_name'] = 'None'
        self.item['listing_date'] = self.item['updated_date'] = '0'

        self.item['listing_by'] = response.meta['agent']
        self.item['name_lister'] = response.meta['name']
        self.item['data_id'] = response.meta['data_id']
        self.item['txn_type'] = response.meta['txn']
        self.item['city'] = response.meta['city']

        self.item['lat'] = response.xpath('//meta[@property="og:latitude"]/@content').extract_first(default='0')

        self.item['longt'] = response.xpath('//meta[@property="og:longitude"]/@content').extract_first(default='0')
        
        self.item['Details'] = response.xpath('//meta[@name="description"]/@content').extract_first(default='None')

        # self.item['data_id'] = response.url.split('/')[1]

        dat = response.xpath('//li[@class="noPrint"]/time/@datetime').extract_first(default='0').split(' ')[0]

        if dat is not '0':
            self.item['listing_date'] = dt.strptime(dat, '%Y-%m-%d').strftime('%m/%d/%Y')

        self.item['updated_date'] = self.item['listing_date']

        conf = response.xpath('//h2[@id="AutoGeneratedTitle"]/text()').extract_first(default='0')

        bed = re.findall('[0-9]', conf)
        if bed:
            self.item['config_type'] = bed[0] + 'BHK'
        if not bed:
            self.item['config_type'] = 'None'

        build = build1 = ''
        try:
            loc = response.xpath('//div[@id="PropertyDetails"]/section/header/h4/text()').extract_first().strip().split(',')
            self.item['locality'] = loc[len(loc) - 2].strip()

            build = response.xpath('//div[@id="PropertyDetails"]/section/header/h3/text()').extract_first()
            build1 = response.xpath('//div[@id="PropertyDetails"]/section/header/h4/text()').extract_first().strip()
        except Exception as e:
            self.item['locality'] = 'None'

        address = response.xpath('//section[@id="PropertySummary"]/header/h4/text()').extract_first(default=self.item['city']).strip().split(',')
        self.item['address'] = address

        buildname = ''

        if 'House' in conf:
            self.item['property_type'] = 'House'
            self.item['Building_name'] = 'None'
        else:
            self.item['property_type'] = 'Apartment'
            buildname = ''
            # response.xpath('//h2[@id="AutoGeneratedTitle"]/text()').extract_first().strip().split(',')[0].split('in ')[1]
            # (response.xpath('//section[@id="PropertySummary"]/header/h4/text()').extract_first().strip()).split(',')[0]
            try:
                try:
                    buildname = response.xpath("//ul[@id='PropertyAttributes']/li[contains(text(),'Society')]/span/a/text()").extract_first().strip()
                except:
                    buildname = response.xpath("//ul[@id='PropertyAttributes']/li[contains(text(),'Society')]/span/text()").extract_first()
            except:
                pass
            if buildname == '' or buildname == ' ' or buildname is None:
                buildname = address[0]
            if 'flat ' in buildname.lower() or 'room ' in buildname.lower() or 'plot ' in buildname.lower() or str(buildname).isdigit() is True:
                buildname = address[1]

            if buildname is not None:
                if len(buildname) > 35:
                    buildname = 'None'
                else:
                    buildname = buildname.strip()
                    if self.item['locality'] in buildname:
                        buildname = ''.join(re.findall(' in (.*)', build))
                    if buildname == '':
                        buildname = ''.join(re.findall(' at (.*)', build))
                        if buildname == '':
                            buildname = ''.join(build1.split(',')[:1]).replace(self.item['locality'], '')

                    if (self.item['city'] in buildname) or (self.item['locality'] in buildname) or (buildname in self.item['locality']):
                        buildname = ''.join(build1.split(',')[:2]).replace(self.item['locality'], '')
                    if buildname == ' ':
                        buildname = 'None'

                    if 'opp' in buildname.lower():
                        buildname = buildname.lower().split('opp')[0]
                    if 'near ' in buildname.lower():
                        buildname = buildname.lower().split('near ')[0]
                    if ' at ' in buildname.lower():
                        buildname = buildname.lower().split(' at ')[1]
                    if ' in ' in buildname.lower():
                        buildname = buildname.lower().split(' in ')[1]
                    if ',' in buildname:
                        if buildname.split(',')[0] == '' or buildname.split(',')[0] == ' ':
                            buildname = buildname.split(',')[1]
                        else:
                            buildname = buildname.split(',')[0]
                    if '.' in buildname or ':' in buildname or ';' in buildname:
                        buildname.replace('.', '').replace(':', '').replace(';', '')

                    buildname = buildname.strip()
                    re.sub('for rent', '', buildname, flags=re.IGNORECASE)
                    re.sub('for sale', '', buildname, flags=re.IGNORECASE)
                    re.sub(' in ', '', buildname, flags=re.IGNORECASE)
                    re.sub('for boys', '', buildname, flags=re.IGNORECASE)
                    re.sub('for girls', '', buildname, flags=re.IGNORECASE)
                    re.sub('bhk', '', buildname, flags=re.IGNORECASE)
                    re.sub('no', '', buildname, flags=re.IGNORECASE)
                    re.sub('room', '', buildname, flags=re.IGNORECASE)
                    re.sub('flat', '', buildname, flags=re.IGNORECASE)
                    re.sub('plot', '', buildname, flags=re.IGNORECASE)
                    re.sub(self.item['locality'], '', buildname, flags=re.IGNORECASE)
                    re.sub(self.item['city'], '', buildname, flags=re.IGNORECASE)
                    buildname = buildname.strip()
        if buildname == self.item['locality'] or buildname == self.item['city'] or buildname == '' or buildname == ' ' or buildname == 'None' or buildname is None:
            self.item['Building_name'] = 'None'
        elif len(buildname) > 35 or str(buildname).isdigit() is True:
            self.item['Building_name'] = 'None'
        else:
            self.item['Building_name'] = buildname.strip()

        if 'for boy' in [conf.lower(), build.lower(), build1.lower()]:
            self.item['management_by_landlord'] = 'Only for Boys'
        elif 'for girl' in [conf.lower(), build.lower(), build1.lower()]:
            self.item['management_by_landlord'] = 'Only for Girls'

        try:
            self.item['areacode'] = re.findall('[0-9]+', address[len(address) - 1])[0]
        except:
            self.item['areacode'] = '0'

        value = response.xpath('//ul[@id="PropertyAttributes"]/li/span/text()').extract()
        try:
            price = response.xpath('//div[@id="PropertyPrice"]/text()').extract()[1].strip()
            if ',' in price:
                price = price.replace(',', '')
            if 'ale' in self.item['txn_type']:
                if 'la' in price:
                    price = price.split(' la')[0]
                    if not '-' in price:
                        self.item['Selling_price'] = str(float(price.split(' ')[0]) * 100000)
                    elif '-' in price:
                        self.item['Selling_price'] = str(float(price.split('-')[-1]) * 100000)
                elif 'crore' in price:
                    price = price.split(' crore')[0]
                    if not '-' in price:
                        self.item['Selling_price'] = str(float(price.split(' ')[0]) * 10000000)
                    elif '-' in price:
                        self.item['Selling_price'] = str(float(price.split('-')[-1]) * 10000000)
                else:
                    if '-' in price:
                        self.item['Selling_price'] = str(price.split('-')[1])
                    else:
                        self.item['Selling_price'] = price
            if 'Rent' in self.item['txn_type']:
                if 'la' in price:
                    price = price.split(' la')[0]
                    if not '-' in price:
                        self.item['Monthly_Rent'] = str(float(price.split(' ')[0]) * 100000)
                    elif '-' in price:
                        self.item['Monthly_Rent'] = str(float(price.split('-')[1]) * 100000)
                elif 'crore' in price:
                    price = price.split(' crore')[0]
                    if not '-' in price:
                        self.item['Monthly_Rent'] = str(float(price.split(' ')[0]) * 10000000)
                    elif '-' in price:
                        self.item['Monthly_Rent'] = str(float(price.split('-')[1]) * 10000000)
                else:
                    if '-' in price:
                        self.item['Monthly_Rent'] = str(price.split('-')[1])
                    else:
                        self.item['Monthly_Rent'] = price
        except Exception as e:
            print(e)

        try:
            price_square = response.xpath("//ul[@id='PropertyAttributes']/li[contains(text(),'Rate')]/span/text()").extract_first(default='0').replace(',', '')
            if 'la' in price_square:
                price_square = str(float(price_square.strip() * 100000))
            if 'cr' in price_square:
                price_square = str(float(price_square.strip() * 10000000))
            self.item['price_per_sqft'] = price_square
        except Exception as e:
            self.item['price_per_sqft'] = 0

        try:
            poss = [pos for pos in value if ('Immediate' in pos) or (('Within' in pos) and ('Year' in pos)) or (('Within' in pos) and ('Month' in pos))][0]
        except:
            poss = 'None'

        if 'Resale' in poss:
            self.item['txn_type'] = 'Resale'

        try:
            if 'ale' in self.item['txn_type']:
                if 'Immediate' in poss:
                    self.item['Possession'] = dt.today().strftime('%m/%d/%Y')
                    self.item['Status'] = 'Ready to move'
                if ('Within' in poss) and ('Year' in poss):
                    poss1 = int(poss.replace('Within ', '').split(' Year')[0])
                    self.item['Possession'] = (dt.today() + relativedelta(years=poss1)).strftime('%m/%d/%Y')
                    self.item['Status'] = 'Under Construction'
                if ('Within' in poss) and ('Month' in poss):
                    poss1 = int(poss.replace('Within ', '').split(' Month')[0])
                    self.item['Possession'] = (dt.today() + relativedelta(months=poss1)).strftime('%m/%d/%Y')
                    self.item['Status'] = 'Under Construction'
            if 'ent' in self.item['txn_type']:
                if 'Immediate' in poss:
                    self.item['Possession'] = dt.today().strftime('%m/%d/%Y')
                if ('Within' in poss) and ('Year' in poss):
                    poss1 = int(poss.replace('Within ', '').split(' Year')[0])
                    self.item['Possession'] = (dt.today() + relativedelta(years=poss1)).strftime('%m/%d/%Y')
                if ('Within' in poss) and ('Month' in poss):
                    poss1 = int(poss.replace('Within ', '').split(' Month')[0])
                    self.item['Possession'] = (dt.today() + relativedelta(months=poss1)).strftime('%m/%d/%Y')
                self.item['Status'] = [stat for stat in value if 'urnish' in stat][0]
        except Exception as e:
            print(e)

        if self.item['Status'] == '' or self.item['Status'] == ' ' or self.item['Status'] is None:
            self.item['Status'] = 'None'

        try:
            Bua_sqft = response.xpath('//span[@class="areaUnit downArrow"]/text()').extract_first(default='0')
            if 'cre' in Bua_sqft:
                Bua_sqft = int(Bua_sqft.split(' ')[0]) * 43560
            else:
                Bua_sqft = Bua_sqft.split(' ')[0]
            self.item['Bua_sqft'] = str(Bua_sqft)
        except:
            self.item['Bua_sqft'] = '0'

        try:
            aged = [age for age in value if 'Year' in age][0]
            if '-' in aged:
                aged = re.findall('[0-9]+', aged.split('-')[1])[0]
            else:
                aged = re.findall('[0-9]+', aged)[0]    
            self.item['age'] = aged
        except:
            self.item['age'] = '0'

        if self.item['age'] is None or self.item['age'] == '' or self.item['age'] == ' ':
            self.item['age'] = '0'

        # if str(self.item['Building_name']).isdigit():
        #     self.item['Building_name'] = 'None'

        self.item['scraped_time'] = dt.now().strftime('%m/%d/%Y')

        if ((not self.item['Monthly_Rent'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['Building_name'] == 'None') and (not self.item['lat'] == '0')) or ((not self.item['Selling_price'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['Building_name'] == 'None') and (not self.item['lat'] == '0')) or ((not self.item['price_per_sqft'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['Building_name'] == 'None') and (not self.item['lat'] == '0')):
            self.item['quality4'] = 1
        elif ((not self.item['price_per_sqft'] == '0') and (not self.item['Building_name'] == 'None') and (not self.item['lat'] == '0')) or ((not self.item['Selling_price'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['lat'] == '0')) or ((not self.item['Monthly_Rent'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['lat'] == '0')) or ((not self.item['Selling_price'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['Building_name'] == 'None')) or ((not self.item['Monthly_Rent'] == '0') and (not self.item['Bua_sqft'] == '0') and (not self.item['Building_name'] == 'None')):
            self.item['quality4'] = 0.5
        else:
            self.item['quality4'] = 0
        if (not self.item['Building_name'] == 'None') and (not self.item['listing_date'] == '0') and (not self.item['txn_type'] == 'None') and (not self.item['property_type'] == 'None') and (not self.item['Selling_price'] == '0' or not self.item['Monthly_Rent'] == '0'):
            self.item['quality1'] = 1
        else:
            self.item['quality1'] = 0

        if (not self.item['Launch_date'] == '0') or (not self.item['Possession'] == '0'):
            self.item['quality2'] = 1
        else:
            self.item['quality2'] = 0

        if (not self.item['mobile_lister'] == 'None') or (not self.item['listing_by'] == 'None') or (not self.item['name_lister'] == 'None'):
            self.item['quality3'] = 1
        else:
            self.item['quality3'] = 0

        yield self.item
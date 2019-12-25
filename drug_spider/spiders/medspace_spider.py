import csv
from pprint import pprint

import requests
import scrapy
from scrapy import Selector


class QuotesSpider(scrapy.Spider):
  def __init__(self):
    drug_url = ''

  name = "medspace_drugs"

  def start_requests(self):
    fieldsnames = ['Medicine name', 'Brand name', 'Class name', 'Dosing & Uses', 'Adverse Effects', 'Warnings', 'Pregnancy & Lactation', 'Absorption', 'Distribution', 'Metabolism', 'Elimination', 'Administration', 'Formulary', 'interactions_minor', 'interactions_serious', 'interactions_contraindicated', 'interactions_monitor_closely', 'PH USES', 'PH HOW TO USE', 'PH SIDE EFFECTS', 'PH PRECAUTIONS', 'PH DRUG INTERACTIONS', 'PH OVERDOSE', 'PH NOTES', 'PH MISSED DOSE', 'PH STORAGE']
    with open('drugs.csv', 'w', newline='') as file:
      writer = csv.DictWriter(file, fieldsnames)
      writer.writeheader()
    urls = [
      'https://reference.medscape.com/drugs',
      # 'https://reference.medscape.com/drug/lotensin-benazepril-342327',
    ]
    for url in urls:
      yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    drug_otcs_herbels = Selector(text=response.body)
    for drug_otcs_herbel in drug_otcs_herbels.xpath('//*[@id="drugdbmain2"]//li/a'):
      url = drug_otcs_herbel.attrib['href']
      print('homepage= ', url)
      yield scrapy.Request(url=url, callback=self.disease_parse)

  def disease_parse(self, response):
    diseases = Selector(text=response.body)
    for disease in diseases.xpath('//*[@id="drugdbmain2"]/ul/li/a'):
      url = disease.attrib['href']
      print('disease_url= ', url)
      yield scrapy.Request(url=url, callback=self.drug_parse)

  def drug_parse(self, response):
    drugs = Selector(text=response.body)
    for drug in drugs.xpath('//*[@id="drugdbmain2"]/ul/li/a'):
      self.drug_url = drug.attrib['href']
      print('drug_url= ', self.drug_url)
      yield scrapy.Request(url=self.drug_url, callback=self.drug_detail_parse)

  def drug_detail_parse(self, response):
    drug_details = Selector(text=response.body)
    ids = drug_details.xpath("//div[contains(@id,'content_')]")
    content_ids = [id.attrib['id'] for id in ids]
    drug_dict = {'Medicine name': '', 'Brand name': '', 'Class name': '', 'Dosing & Uses': '',
                 'Adverse Effects': '', 'Warnings': '', 'Pregnancy & Lactation': '', 'Absorption': '',
                 'Distribution': '', 'Metabolism': '', 'Elimination': '', 'Administration': '',
                 'Formulary': '', 'interactions_minor': '', 'interactions_serious': '',
                 'interactions_contraindicated': '', 'interactions_monitor_closely': '', 'PH USES': '',
                 'PH HOW TO USE': '', 'PH SIDE EFFECTS': '', 'PH PRECAUTIONS': '', 'PH DRUG INTERACTIONS': '',
                 'PH OVERDOSE': '', 'PH NOTES': '', 'PH MISSED DOSE': '', 'PH STORAGE': ''}

    try:
      drug_dict.update(
        {'Medicine name': drug_details.xpath('//*[@id="maincolboxdrugdbheader"]/h1/span/text()').extract()[0]})
    except:
      pass

    try:
      drug_dict.update(
        {'Brand name': drug_details.xpath('//*[@id="maincolboxdrugdbheader"]/div[2]/span/text()').extract()[0]})
    except:
      pass

    try:
      drug_dict.update(
        {'Class name': drug_details.xpath('//*[@id="maincolboxdrugdbheader"]/ul/li/a/text()').extract()[0]})
    except:
      pass
    try:
      for id in content_ids:
        header = drug_details.xpath(f'//*[@id="{id}"]/h2/text()').extract()
        try:
          if header[0] == 'Dosing & Uses':
            string = str([drug_details.xpath(f'//*[@id="dose_adult"]/div/ul/li[{i + 1}]/text()').extract()[0] for i in
                          range(len(drug_details.xpath('//*[@id="dose_adult"]/div/ul/li')))]) + '\n'
            for i in range(len(drug_details.xpath('//*[@id="dose_adult"]/h3'))):
              string += drug_details.xpath(f'//*[@id="dose_adult"]/h3[{i + 1}]/text()').extract()[0] + '\n'
              string += str([drug_details.xpath(f'//*[@id="dose_adult"]/p[{i + 1}]/text()').extract()[0]
                             for i in range(len(drug_details.xpath('//*[@id="dose_adult"]/p')))]) + '\n'
            drug_dict.update({header[0]: str(string)})
        except:
          pass

        try:
          if header[0] == 'Adverse Effects':
            string = ''
            string += str([drug_details.xpath(f'//*[@id="content_4"]/div[1]/p[{j + 1}]/text()').extract()[0] for j in
                           range(len(drug_details.xpath(f'//*[@id="content_4"]/div[1]/p')))]) + '\n'
            drug_dict.update({header[0]: string})
        except:
          print('error in Adverse Effects')

        try:
          if header[0] == 'Warnings':
            string = ''
            for i in range(len(drug_details.xpath('//*[@id="content_5"]/div[1]/div/h3'))):
              string += drug_details.xpath('//*[@id="content_5"]/div[1]/div/h3/text()').extract()[0] + '\n'
              string += str([drug_details.xpath(f'//*[@id="content_5"]/div[1]/div/p[{j + 1}]/text()').extract()[0]
                             for j in range(len(drug_details.xpath('//*[@id="content_5"]/div[1]/div/p')))])
            drug_dict.update({header[0]: string})
        except:
          print('error in Warnings')

        try:
          if header[0] == 'Pregnancy & Lactation':
            string = ''
            for i in range(len(drug_details.xpath('//*[@id="content_6"]/div[1]/h3'))):
              string += drug_details.xpath(f'//*[@id="content_6"]/div[1]/h3[{i + 1}]/text()').extract()[0] + '\n'
              string += drug_details.xpath(f'//*[@id="content_6"]/div[1]/p[{i + 1}]/text()').extract()[0] + '\n'
            drug_dict.update({header[0]: string})
        except:
          print('error in Pregnancy & Lactation')

        try:
          if header[0] == 'Pharmacology':
            string = ''
            for i in range(len(drug_details.xpath('//*[@id="content_10"]/div[1]/h3'))):
              name = drug_details.xpath(f'//*[@id="content_10"]/div[1]/h3[{i + 1}]/text()').extract()[0]
              # string += drug_details.xpath(f'//*[@id="content_10"]/div[1]/h3[{i + 1}]/text()').extract()[0] + '\n'
              # string += drug_details.xpath(f'//*[@id="content_10"]/div[1]/p[{i + 1}]/text()').extract()[0] + '\n'
              if name in ['Absorption', 'Distribution', 'Metabolism', 'Elimination']:
                drug_dict.update(
                  {name: drug_details.xpath(f'//*[@id="content_10"]/div[1]/p[{i + 1}]/text()').extract()[0]})
                string += drug_details.xpath(f'//*[@id="content_10"]/div[1]/p[{i + 1}]/text()').extract()[0] + '\n'
            drug_dict.update({header[0]: string})
        except:
          print('error in Pharmacology')

        try:
          if header[0] == 'Administration':
            string = ''
            for i in range(len(drug_details.xpath('//*[@id="content_11"]/div[1]/h3'))):
              string += drug_details.xpath(f'//*[@id="content_11"]/div[1]/h3[{i + 1}]/text()').extract()[0] + '\n'
              string += str([drug_details.xpath(f'//*[@id="content_11"]/div[{i + 1}]/p[{j + 1}]/text()').extract()
                             for j in range(len(drug_details.xpath('//*[@id="content_11"]/div[1]/p')))])
            drug_dict.update({header[0]: str(string)})
        except:
          print('error in Administration')

        try:
          if header[0] == 'Formulary':
            string = drug_details.xpath('//*[@id="fs_tabs_content"]/p/text()').extract()[0]
            drug_dict.update({header[0]: str(string)})
        except:
          pass

        try:
          if header[0] == 'Interactions':
            interactions = \
              requests.get(
                f'https://reference.medscape.com/druginteraction.do?action=getDrugs&id={self.drug_url.split("-")[-1]}').json()
            if interactions.get('errorCode') == 1:
              minor = list()
              monitor_closly = list()
              serious = list()
              contraindicated = list()
              for key, value in interactions.get('interactions').items():
                if value.get('severity') == "Monitor Closely":
                  monitor_closly.append({value.get('object', 'unknown'): value.get('text', None)})
                elif value.get('severity') == "Minor":
                  minor.append({value.get('object', 'unknown'): value.get('text', None)})
                elif value.get('severity') == "Serious - Use Alternative":
                  serious.append({value.get('object', 'unknown'): value.get('text', None)})
                elif value.get('severity') == "Contraindicated":
                  contraindicated.append({value.get('object', 'unknown'): value.get('text', None)})
              drug_dict.update({'interactions_minor': str(minor), 'interactions_serious': str(serious),
                                'interactions_contraindicated': str(contraindicated), 'interactions_monitor_closely':
                                  str(monitor_closly)})
        except:
          print('error in Interactions')

        try:
          if header[0] == 'Patient Handout':
            drug_id = requests.get(
              f'https://reference.medscape.com/patienthandout.do?action=getRoutedDrugs&contentId={self.drug_url.split("-")[-1]}').json()[
              'routedDrugsList'][0].get('id')
            patient_handout = \
              requests.get(
                f'https://reference.medscape.com/patienthandout.do?action=getPatientHandout&routedDrugId={drug_id}')
            html_str = Selector(text=patient_handout.json()['patientHandout'].get('text'))
            input(html_str)
            for i in range(len(html_str.xpath('/html/body/p'))):
              input()
              input(html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0])
              input(html_str.xpath(f'/html/body/p[{i + 1}]/span/'))
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'USES:':
                drug_dict.update({'PH USES': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'HOW TO USE:':
                drug_dict.update({'PH HOW TO USE': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'SIDE EFFECTS:':
                drug_dict.update({'PH SIDE EFFECTS': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'SIDE EFFECTS:':
                drug_dict.update({'PH SIDE EFFECTS': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'PRECAUTIONS:':
                drug_dict.update({'PH PRECAUTIONS': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'DRUG INTERACTIONS:':
                drug_dict.update({'PH DRUG INTERACTIONS': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'OVERDOSE:':
                drug_dict.update({'PH OVERDOSE': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'NOTES:':
                drug_dict.update({'PH NOTES': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'MISSED DOSE:':
                drug_dict.update({'PH MISSED DOSE': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
              if html_str.xpath(f'/html/body/p[{i + 1}]/span/text()').extract()[0] == 'STORAGE:':
                drug_dict.update({'PH STORAGE': html_str.xpath(f'/html/body/p[{i + 1}]/text()').extract()[0]})
        except:
          print('error in patient handout')

        pprint(drug_dict)
      with open('drugs.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, list(drug_dict.keys()))
        writer.writerow(drug_dict)
    except:
      pass

# -*- coding: utf-8 -*-
import json
import os
import urllib
import logging
MAPPER_TEMPLATE = "http://im.govwizely.com/api/terms.json?mapped_term=%s&source=%s&log_failed=true"
TAXONOMY_TEMPLATE = "https://api.trade.gov/ita_taxonomies/search.json?size=1&types=Countries&api_key=DoC9TUgIck11HgwBdIvcd-RV&q=%s"

class TaxonomyMapper:
  def __init__(self, options):
    self.config_array = options['config']
    self.mapper_source = options['mapper_source']
    self.request_cache = {}

  def add_taxonomy_fields(self, entry):
    for config in self.config_array:
      term = None
      entry[config['desired_field']] = ''
      mapper_response = self.cached_response_for(MAPPER_TEMPLATE % (entry[config['starting_field']], self.mapper_source))
      
      if len(mapper_response) > 0:
        term = mapper_response[0]
      if self.country_should_be_added(term, config):
        entry[config['desired_field']] = term["name"]
      elif self.world_regions_should_be_added(term, config):
        entry[config['desired_field']] = self.add_world_region(term, mapper_response)
    return entry

  def add_world_region(self, term, mapper_response):
    if "Countries" in term["taxonomies"]:
      country = term["name"]
     
      taxonomy_response = self.cached_response_for(TAXONOMY_TEMPLATE % country)
      return taxonomy_response["results"][0]["object_properties"]["has_broader"][0]["label"]
    elif "World Regions" in term["taxonomies"]:
      return [term["name"] for term in mapper_response]
    else:
      return ""

  def country_should_be_added(self, term, config):
    return term is not None and config['desired_field'] == "country" and "Countries" in term["taxonomies"]

  def world_regions_should_be_added(self, term, config):
    return term is not None and config['desired_field'] == "world_region"

  def cached_response_for(self, url):
    if url in self.request_cache:
      return self.request_cache[url]
    else:
      url = url.replace(' ', '%20')
      response = json.loads(urllib.request.urlopen(url).read())
      self.request_cache[url] = response
      return response
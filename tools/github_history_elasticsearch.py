#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inserts the GitHub history of a project into an Elasticsearch instance."""

from __future__ import unicode_literals
import json
import elasticsearch
import argparse
import requests


class ElasticCommitInserter(object):

  def __init__(self, host='localhost', port=9200, index='commits'):
    super(ElasticCommitInserter, self).__init__()
    self._client = elasticsearch.Elasticsearch([{'host': host, 'port': port}])
    self._index_name = index
    self._doc_type = 'commit'
    self._CreateIndex()
    self._UpdateMapping()

  def AddCommit(self, commit):
    identifier = commit['sha']
    timestamp = commit['commit']['committer']['date']
    commit['@timestamp'] = timestamp
    commit['project_path'] = self.project_path
    try:
      resource = self._client.index(
          index=self._index_name, doc_type=self._doc_type, body=commit,
          id=identifier)
    except elasticsearch.exceptions.RequestError as exception:
      print(exception)
      return

    print(resource)

  def _CreateIndex(self):
    if not self._client.indices.exists(self._index_name):
      self._client.indices.create(self._index_name)

  def _UpdateMapping(self):
    self._client.indices.put_mapping(
        index=self._index_name,
        doc_type=self._doc_type,
        body={
          "properties": {
            "project_path": {
              "type": "keyword",
              "doc_values": True
            }
          }
        })


class GithubFetcher(object):
  """Fetches commit history for a GitHub project"""

  def __init__(self, organisation, project):
    self.project = project
    self.organization = organisation

  def GetCommits(self):
    request = requests.get(
        'https://api.github.com/repos/{0:s}/commits?sha=master'.format(
            self.project_path))
    if not request.ok:
      return []
    commit_documents = json.loads(request.content)
    return commit_documents

  def BuildCommitDocument(self, commit):
    timestamp = commit['commit']['committer']['date']
    commit['@timestamp'] = timestamp
    commit['project_path'] = self.project_path
    return commit


if __name__ == '__main__':
  argument_parser = argparse.ArgumentParser()

  argument_parser.add_argument('--host', type=str, default='localhost',
      help='hostname or IP address of the elasticsearch server.')

  argument_parser.add_argument('--project', type=str,
      default='plaso',
      help='Github project name (eg. plaso).')

  options = argument_parser.parse_args()

  inserter = ElasticCommitInserter(host=options.host)
  fetcher = GithubFetcher(project_path=options.project_path)
  commits = fetcher.GetCommits()
  for commit in commits:
    commit_document = fetcher.BuildCommitDocument(commit)
    inserter.AddCommit(commit_document)

import os
from google.cloud import monitoring
from google.cloud.monitoring import Client
from google.cloud.monitoring import Metric
from google.cloud.monitoring import MetricDescriptor
from google.cloud.monitoring import MetricKind, ValueType
from google.cloud.monitoring import LabelValueType
from google.cloud.monitoring import LabelDescriptor
from google.cloud.monitoring import Resource
from opencensus.stats import view
from datetime import datetime
from datetime import timedelta

class StackDriverExporter(object):
    def __init__(self, client=None, project_id=None, resource=None):
        if client is None:
            client = Client(project=project_id)

        self.client = client
        self.project_id = client.project
        self.resource = client.resource('global', {})

    def emit(self, views, datapoint=None):
        name = 'projects/{}'.format(self.project_id)
        '''metric = {}'''
        metrics = self.translate_to_stackdriver(views)
        for metric_type, metric_label in metrics.items():
            metric = self.client.metric(metric_type, metric_label)
            descriptor = self.client.metric_descriptor(metric_type, monitoring.MetricKind.CUMULATIVE, monitoring.ValueType.INT64, description=metric_label)
            descriptor.create()
            self.client.resource = self.set_resource(type_='global', labels= {'project_id': self.project_id})
            self.client.write_point(metric, self.client.resource, datapoint, datetime.utcnow() + timedelta(seconds=60), datetime.utcnow())
            self.client.time_series(metric, self.client.resource, datapoint, datetime.utcnow() + timedelta(seconds=60), datetime.utcnow())
            return 'Successfully wrote time series.'

    def set_resource(self, type_, labels):
        return self.client.resource(type_, labels)

    def translate_to_stackdriver(self, views):
        metrics = {}
        labels = []
        for v in views or []:
            metric_type = v.View.name
            metric_label = v.view.get_description()
            metrics[metric_type] = metric_label
            labels.append(metric_label)
        return metrics











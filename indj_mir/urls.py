"""InDJ_MIR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from indj_mir.com.indj.mir.controllers import FastDTWController
from indj_mir.com.indj.mir.controllers import FeaturesController
from indj_mir.com.indj.mir.controllers import YoutubeController
from indj_mir.com.indj.mir.controllers import ChannelController
from indj_mir.com.indj.mir.controllers import GeoLocationController
from indj_mir.com.indj.mir.controllers import CrawlController

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^batches/', FastDTWController.execute_all_songs),
    url(r'^compare/source_uid/', FastDTWController.execute_source_uid),
    url(r'^features/extract/all/', FeaturesController.extract_all_features),
    url(r'^features/extract/source_uid/', FeaturesController.extract_source_uid),
    url(r'^mp3/download/all/', YoutubeController.download_all_mp3_songs),
    url(r'^mp3/download/text_search/', YoutubeController.download_one_mp3),
    url(r'^features/training/', FeaturesController.training_regression),
    url(r'^channel/recommend/', ChannelController.recommend),
    url(r'^batch/channel/recommend/', ChannelController.runbatch_recommend),
    url(r'^batch/channel/aggregate/', ChannelController.runbatch_aggregate_channel),
    url(r'^batch/geolocation/cluster/', GeoLocationController.runbatch_cluster_geolocation),
    url(r'^geolocation/import/data/', GeoLocationController.import_geolocation_data),
    url(r'^channel/crawl/image/', CrawlController.crawl_channel_image),
    url(r'^song/crawl/torrent', CrawlController.crawl_song_torrent),
]

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random

from google.appengine.ext import db
# TODO from google.appengine.api import memcache

from migrationmodel import MigratingModel, get_by_pk

NOTIFY_NONE = 0
NOTIFY_ONCE = 1
NOTIFY_ALL = 2

NOTIFY_TYPE_COUNT = 3


class Phone(MigratingModel):
    migration_version = 1

    phone_type = db.StringProperty(required=True)
    phone_uid = db.StringProperty(required=True)
    phone_token = db.StringProperty()
    account_id = db.StringProperty()

    pk = ['phone_type', 'phone_uid']


class Account(MigratingModel):
    migration_version = 1

    account_id = db.StringProperty(required=True)
    to_date = db.DateTimeProperty(default=None)
    subscription_type = db.StringProperty()
    expiration_date = db.DateProperty()
    transaction_id = db.StringProperty()
    receipt_data = db.TextProperty()

    pk = ['account_id', 'to_date']


class ParticipantPreferences(MigratingModel):
    migration_version = 3

    participant = db.StringProperty(required=True)
    notify = db.BooleanProperty(default=True)
    notify_initial = db.BooleanProperty(default=True)
    email = db.StringProperty()
    activation = db.StringProperty()
    preferences_wave_id = db.StringProperty()
    account_id = db.StringProperty()

    pk = ['participant']

    preferencesWaveId = db.StringProperty(default=None) # Deprecated use preferences_wave_id

    def __init__(self, *args, **kwds):
        self.activation = random_activation()
        super(ParticipantPreferences, self).__init__(*args, **kwds)

    def put(self, *args, **kwds):
        # TODO memcache.set(self.get_key(), self, namespace='pp')
        super(ParticipantPreferences, self).put(*args, **kwds)

    def migrate_1(self):
        if self.notify_initial == None:
            self.notify_initial = True

    def migrate_2(self):
        if self.activation == None:
            self.activation = random_activation()

    def migrate_3(self):
        if self.preferencesWaveId:
            self.preferences_wave_id = self.preferencesWaveId;


class ParticipantWavePreferences(MigratingModel):
    migration_version = 2

    participant = db.StringProperty(required=True)
    wave_id = db.StringProperty(required=False) # TODO migrate all entities
    notify_type = db.IntegerProperty(default=NOTIFY_NONE)
    visited = db.BooleanProperty(default=False)
    last_visited = db.DateTimeProperty()

    pk = ['participant', 'wave_id']

    waveId = db.StringProperty(default=None) # Deprecated use wave_id
    notify = db.BooleanProperty(default=None) # Deprecated use notify_type

    #def put(self, *args, **kwds):
    #    TODO
    #    memcache.set(self.get_key(), self, namespace='pwp')
    #    super(ParticipantWavePreferences, self).put(*args, **kwds)

    def migrate_1(self):
        if self.notify != None:
            if self.notify:
                self.notify_type = NOTIFY_ALL
            self.notify = None

    def migrate_2(self):
        if self.waveId:
            self.wave_id = self.waveId;

    @classmethod
    def get_by_pk(cls, *args, **kw):
        o = get_by_pk(cls, *args, **kw)
        if not o:
            q = ParticipantWavePreferences.all()
            q.filter('participant =', args[0])
            q.filter('waveId =', args[1])
            o = q.get()
        return o


class ApplicationSettings(MigratingModel):
    migration_version = 0

    keyname = db.StringProperty(required=True)
    value = db.StringProperty()

    pk = ['keyname']

    @classmethod
    def get(cls, keyname):
        return cls.get_by_pk(keyname).value


def random_activation():
    return ''.join([str(random.randint(0, 9)) for a in range(9)])

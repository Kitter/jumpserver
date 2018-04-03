#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging

from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _

from common.utils import get_signer
from ..const import SYSTEM_USER_CONN_CACHE_KEY
from .base import AssetUser


__all__ = ['AdminUser', 'SystemUser',]
logger = logging.getLogger(__name__)
signer = get_signer()


class AdminUser(AssetUser):
    """
    A privileged user that ansible can use it to push system user and so on
    """
    BECOME_METHOD_CHOICES = (
        ('sudo', 'sudo'),
        ('su', 'su'),
    )
    become = models.BooleanField(default=True)
    become_method = models.CharField(choices=BECOME_METHOD_CHOICES, default='sudo', max_length=4)
    become_user = models.CharField(default='root', max_length=64)
    _become_pass = models.CharField(default='', max_length=128)

    def __str__(self):
        return self.name

    @property
    def become_pass(self):
        password = signer.unsign(self._become_pass)
        if password:
            return password
        else:
            return ""

    @become_pass.setter
    def become_pass(self, password):
        self._become_pass = signer.sign(password)

    @property
    def become_info(self):
        if self.become:
            info = {
                "method": self.become_method,
                "user": self.become_user,
                "pass": self.become_pass,
            }
        else:
            info = None
        return info

    def get_related_assets(self):
        assets = self.asset_set.all()
        return assets

    @property
    def assets_amount(self):
        return self.get_related_assets().count()

    class Meta:
        ordering = ['name']
        verbose_name = _("Admin user")

    @classmethod
    def generate_fake(cls, count=10):
        from random import seed
        import forgery_py
        from django.db import IntegrityError

        seed()
        for i in range(count):
            obj = cls(name=forgery_py.name.full_name(),
                      username=forgery_py.internet.user_name(),
                      password=forgery_py.lorem_ipsum.word(),
                      comment=forgery_py.lorem_ipsum.sentence(),
                      created_by='Fake')
            try:
                obj.save()
                logger.debug('Generate fake asset group: %s' % obj.name)
            except IntegrityError:
                print('Error continue')
                continue


class SystemUser(AssetUser):
    SSH_PROTOCOL = 'ssh'
    RDP_PROTOCOL = 'rdp'
    PROTOCOL_CHOICES = (
        (SSH_PROTOCOL, 'ssh'),
        (RDP_PROTOCOL, 'rdp'),
    )

    nodes = models.ManyToManyField('assets.Node', blank=True, verbose_name=_("Nodes"))
    priority = models.IntegerField(default=10, verbose_name=_("Priority"))
    protocol = models.CharField(max_length=16, choices=PROTOCOL_CHOICES, default='ssh', verbose_name=_('Protocol'))
    auto_push = models.BooleanField(default=True, verbose_name=_('Auto push'))
    sudo = models.TextField(default='/sbin/ifconfig', verbose_name=_('Sudo'))
    shell = models.CharField(max_length=64,  default='/bin/bash', verbose_name=_('Shell'))

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'protocol': self.protocol,
            'priority': self.priority,
            'auto_push': self.auto_push,
        }

    @property
    def assets(self):
        assets = set()
        for node in self.nodes.all():
            assets.update(set(node.get_all_assets()))
        return assets

    @property
    def assets_connective(self):
        _result = cache.get(SYSTEM_USER_CONN_CACHE_KEY.format(self.name), {})
        return _result

    @property
    def unreachable_assets(self):
        return list(self.assets_connective.get('dark', {}).keys())

    @property
    def reachable_assets(self):
        return self.assets_connective.get('contacted', [])

    def is_need_push(self):
        if self.auto_push and self.protocol == self.__class__.SSH_PROTOCOL:
            return True
        else:
            return False

    class Meta:
        ordering = ['name']
        verbose_name = _("System user")

    @classmethod
    def generate_fake(cls, count=10):
        from random import seed
        import forgery_py
        from django.db import IntegrityError

        seed()
        for i in range(count):
            obj = cls(name=forgery_py.name.full_name(),
                      username=forgery_py.internet.user_name(),
                      password=forgery_py.lorem_ipsum.word(),
                      comment=forgery_py.lorem_ipsum.sentence(),
                      created_by='Fake')
            try:
                obj.save()
                logger.debug('Generate fake asset group: %s' % obj.name)
            except IntegrityError:
                print('Error continue')
                continue



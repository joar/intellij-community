# -*- coding: utf-8 -*-

from __future__ import absolute_import

import contextlib
import copy
import threading
import uuid

ctx = threading.local()


class TrackerBase(object):
    def __init__(self, client=None, server=None):
        self.client = client
        self.server = server

    def handle(self, header):
        ctx.header = header
        ctx.counter = 0

    def gen_header(self, header):
        header.request_id = self.get_request_id()

        if not hasattr(ctx, "counter"):
            ctx.counter = 0

        ctx.counter += 1

        if hasattr(ctx, "header"):
            header.seq = "{prev_seq}.{cur_counter}".format(
                prev_seq=ctx.header.seq, cur_counter=ctx.counter)
            header.meta = ctx.header.meta
        else:
            header.meta = {}
            header.seq = str(ctx.counter)

        if hasattr(ctx, "meta"):
            header.meta.update(ctx.meta)

    def record(self, header, exception):
        pass

    @classmethod
    @contextlib.contextmanager
    def counter(cls, init=0):
        """Context for manually setting counter of seq number.

        :init: init value
        """
        if not hasattr(ctx, "counter"):
            ctx.counter = 0

        old = ctx.counter
        ctx.counter = init

        try:
            yield
        finally:
            ctx.counter = old

    @classmethod
    @contextlib.contextmanager
    def annotate(cls, **kwargs):
        ctx.annotation = kwargs
        try:
            yield ctx.annotation
        finally:
            del ctx.annotation

    @classmethod
    @contextlib.contextmanager
    def add_meta(cls, **kwds):
        if hasattr(ctx, 'meta'):
            old_dict = copy.copy(ctx.meta)
            ctx.meta.update(kwds)
            try:
                yield ctx.meta
            finally:
                ctx.meta = old_dict
        else:
            ctx.meta = kwds
            try:
                yield ctx.meta
            finally:
                del ctx.meta

    @property
    def meta(self):
        meta = ctx.header.meta if hasattr(ctx, "header") else {}
        if hasattr(ctx, "meta"):
            meta.update(ctx.meta)
        return meta

    @property
    def annotation(self):
        return ctx.annotation if hasattr(ctx, "annotation") else {}

    def get_request_id(self):
        if hasattr(ctx, "header"):
            return ctx.header.request_id
        return str(uuid.uuid4())

    def init_handshake_info(self, handshake_obj):
        pass

    def handle_handshake_info(self, handshake_obj):
        pass


class ConsoleTracker(TrackerBase):
    def record(self, header, exception):
        print(header)

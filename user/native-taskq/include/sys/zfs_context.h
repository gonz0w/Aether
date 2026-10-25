// SPDX-License-Identifier: CDDL-1.0
/*
 * CDDL HEADER START
 *
 * The contents of this file are subject to the terms of the
 * Common Development and Distribution License (the "License").
 * You may not use this file except in compliance with the License.
 *
 * You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
 * or https://opensource.org/licenses/CDDL-1.0.
 * See the License for the specific language governing permissions
 * and limitations under the License.
 *
 * When distributing Covered Code, include this CDDL HEADER in each
 * file and include the License file at usr/src/OPENSOLARIS.LICENSE.
 * If applicable, add the following below this CDDL HEADER, with the
 * fields enclosed by brackets "[]" replaced with your own identifying
 * information: Portions Copyright [yyyy] [name of copyright owner]
 *
 * CDDL HEADER END
 */
/*
 * Copyright (c) 2005, 2010, Oracle and/or its affiliates. All rights reserved.
 * Copyright 2011 Nexenta Systems, Inc.  All rights reserved.
 * Copyright (c) 2012, 2018 by Delphix. All rights reserved.
 * Copyright (c) 2012, Joyent, Inc. All rights reserved.
 */

/* Taskq-only native fixture adaptation; types use pinned musl, not glibc.
 * Derived taskq structures below retain upstream CDDL terms. */
#ifndef AETHER_TASKQ_CONTEXT_H
#define AETHER_TASKQ_CONTEXT_H
#include <pthread.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <unistd.h>
#include <time.h>
typedef unsigned int uint_t;
typedef int pri_t;
typedef int boolean_t;
typedef void kthread_t;
typedef uintptr_t taskqid_t;
typedef void task_func_t(void *);
typedef struct {
    pthread_mutex_t m_lock;
    pthread_t m_owner;
} kmutex_t;
typedef struct {
    pthread_rwlock_t rw_lock;
    pthread_t rw_owner;
    uint_t rw_readers;
} krwlock_t;
typedef pthread_cond_t kcondvar_t;
#define TASKQ_NAMELEN 31
typedef struct taskq_ent {
    struct taskq_ent *tqent_next;
    struct taskq_ent *tqent_prev;
    task_func_t *tqent_func;
    void *tqent_arg;
    uintptr_t tqent_flags;
} taskq_ent_t;

typedef struct taskq {
    char tq_name[TASKQ_NAMELEN + 1];
    kmutex_t tq_lock;
    krwlock_t tq_threadlock;
    kcondvar_t tq_dispatch_cv;
    kcondvar_t tq_wait_cv;
    kthread_t **tq_threadlist;
    int tq_flags;
    int tq_active;
    int tq_nthreads;
    int tq_nalloc;
    int tq_minalloc;
    int tq_maxalloc;
    kcondvar_t tq_maxalloc_cv;
    int tq_maxalloc_wait;
    taskq_ent_t *tq_freelist;
    taskq_ent_t tq_task;
} taskq_t;

#define TQENT_FLAG_PREALLOC 1
#define TASKQ_PREPOPULATE 1
#define TASKQ_CPR_SAFE 2
#define TASKQ_DYNAMIC 4
#define TASKQ_THREADS_CPU_PCT 8
#define TASKQ_DC_BATCH 16
#define KM_SLEEP 0x100
#define KM_NOSLEEP 0
#define TQ_NOSLEEP KM_NOSLEEP
#define TQ_SLEEP KM_SLEEP
#define TQ_FRONT 8
#define B_FALSE 0
#define RW_READER 0
#define RW_WRITER 1
#define RW_DEFAULT 0
#define MUTEX_DEFAULT 0
#define CV_DEFAULT 0
#define TS_RUN 0x00000002
#define minclsyspri 19
#define maxclsyspri -20
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
_Noreturn void aether_taskq_fail(unsigned);
#define ASSERT(x)                                                              \
    do {                                                                       \
        if (!(x))                                                              \
            aether_taskq_fail(301);                                            \
    } while (0)
#define VERIFY(x) ASSERT(x)
#define VERIFY0(x) ASSERT((x) == 0)
#define ASSERT3S(a, op, b) ASSERT((a)op(b))
#define VERIFY3S(a, op, b) ASSERT3S(a, op, b)
void *aether_taskq_alloc(size_t, int);
void aether_taskq_free(void *, size_t);
#define kmem_alloc(s, f) aether_taskq_alloc(s, f)
#define kmem_zalloc(s, f) aether_taskq_alloc(s, f)
#define kmem_free(p, s) aether_taskq_free(p, s)
kthread_t *aether_taskq_start(const char *, void (*)(void *), void *);
#define thread_create_named(n, stk, sz, fn, arg, len, proc, state, pri)        \
    aether_taskq_start(n, fn, arg)
#define thread_exit() pthread_exit(NULL)
clock_t aether_taskq_forbidden_ticks(void);
long aether_taskq_sysconf(int);
#define sysconf aether_taskq_sysconf
#define ddi_get_lbolt() aether_taskq_forbidden_ticks()
#define hz                                                                     \
    119 /* Retained upstream constant; throttle sampling is forbidden.         \
         */
void mutex_init(kmutex_t *, char *, int, void *);
void mutex_destroy(kmutex_t *);
void mutex_enter(kmutex_t *);
void mutex_exit(kmutex_t *);
void rw_init(krwlock_t *, char *, int, void *);
void rw_destroy(krwlock_t *);
void rw_enter(krwlock_t *, int);
void rw_exit(krwlock_t *);
void cv_init(kcondvar_t *, char *, int, void *);
void cv_destroy(kcondvar_t *);
void cv_wait(kcondvar_t *, kmutex_t *);
int cv_timedwait(kcondvar_t *, kmutex_t *, clock_t);
void cv_signal(kcondvar_t *);
void cv_broadcast(kcondvar_t *);
extern int taskq_now;
extern taskq_t *system_taskq, *system_delay_taskq;
taskq_t *taskq_create(const char *, int, pri_t, int, int, uint_t);
void taskq_destroy(taskq_t *);
taskqid_t taskq_dispatch(taskq_t *, task_func_t, void *, uint_t);
taskqid_t taskq_dispatch_delay(taskq_t *, task_func_t, void *, uint_t, clock_t);
int taskq_cancel_id(taskq_t *, taskqid_t, boolean_t);
void taskq_wait(taskq_t *);
void taskq_wait_id(taskq_t *, taskqid_t);
taskq_t *taskq_of_curthread(void);
void aether_taskq_tsd_init(void);
void aether_taskq_tsd_fini(void);
#endif

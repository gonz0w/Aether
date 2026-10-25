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
 * Copyright (c) 2012, 2018 by Delphix. All rights reserved.
 * Copyright (c) 2016 Actifio, Inc. All rights reserved.
 * Copyright (c) 2025, Klara, Inc.
 */

/* Reviewed replacements inserted into the pinned libzpool kernel.c.
 * lbolt is gethrtime() >>23; hz remains the upstream approximate conversion.
 * These elapsed requests never use calendar time. */
void cv_init(kcondvar_t *cv, char *name, int type, void *arg)
{
    (void)name, (void)type, (void)arg;
    pthread_condattr_t attr;
    VERIFY0(pthread_condattr_init(&attr));
    VERIFY0(pthread_condattr_setclock(&attr, CLOCK_MONOTONIC));
    VERIFY0(pthread_cond_init(cv, &attr));
    VERIFY0(pthread_condattr_destroy(&attr));
}

static void cv_deadline(time_t seconds, long nanoseconds, struct timespec *ts)
{
    if (seconds < 0 || nanoseconds < 0 || nanoseconds >= NANOSEC ||
        seconds > LLONG_MAX / NANOSEC)
        _Exit(125);
    hrtime_t delta = seconds * NANOSEC;
    if (nanoseconds > LLONG_MAX - delta)
        _Exit(125);
    delta += nanoseconds;
    hrtime_t now = gethrtime();
    if (now > LLONG_MAX - delta)
        _Exit(125);
    hrtime_t deadline = now + delta;
    ts->tv_sec = deadline / NANOSEC;
    ts->tv_nsec = deadline % NANOSEC;
}

int cv_timedwait(kcondvar_t *cv, kmutex_t *mp, clock_t abstime)
{
    clock_t now = ddi_get_lbolt();
    if (now < 0)
        _Exit(125);
    if (abstime <= now)
        return -1;
    if (abstime > (LLONG_MAX >> 23))
        _Exit(125);
    hrtime_t deadline = (hrtime_t)abstime * (1LL << 23);
    struct timespec ts = {deadline / NANOSEC, deadline % NANOSEC};
    memset(&mp->m_owner, 0, sizeof(pthread_t));
    int error = pthread_cond_timedwait(cv, &mp->m_lock, &ts);
    mp->m_owner = pthread_self();
    if (error == ETIMEDOUT)
        return -1;
    VERIFY0(error);
    return 1;
}

int cv_timedwait_hires(kcondvar_t *cv, kmutex_t *mp, hrtime_t tim, hrtime_t res,
                       int flag)
{
    (void)res;
    if (flag != 0 && flag != CALLOUT_FLAG_ABSOLUTE)
        _Exit(125);
    if (tim <= 0)
        return -1;
    struct timespec ts;
    if (flag == CALLOUT_FLAG_ABSOLUTE) {
        if (tim <= gethrtime())
            return -1;
        ts = (struct timespec){tim / NANOSEC, tim % NANOSEC};
    } else {
        cv_deadline(tim / NANOSEC, tim % NANOSEC, &ts);
    }
    memset(&mp->m_owner, 0, sizeof(pthread_t));
    int error = pthread_cond_timedwait(cv, &mp->m_lock, &ts);
    mp->m_owner = pthread_self();
    if (error == ETIMEDOUT)
        return -1;
    VERIFY0(error);
    return 1;
}

void delay(clock_t ticks)
{
    if (ticks < 0 || ticks > (LLONG_MAX >> 23))
        _Exit(125);
    if (!ticks)
        return;
    hrtime_t duration = (hrtime_t)ticks * (1LL << 23);
    struct timespec req = {duration / NANOSEC, duration % NANOSEC};
    if (nanosleep(&req, NULL) != 0)
        _Exit(125);
}

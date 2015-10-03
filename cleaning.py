from askbot.models import User, PostRevision
from stopforumspam.models import Cache


def block_ips(ips):
    for ip in ips:
        if ip == '0.0.0.0':
            continue
        caches = Cache.objects.filter(ip=ip)
        if caches.count() > 1:
            for cache in caches[1:]:
                cache.delete()
        elif caches.count() == 0:
            Cache(ip=ip).save()


def delete_users(users):
    i = 0
    ips = set()
    for u in users:
        for r in u.postrevisions.all():
            ips.add(r.ip_addr)
        try:
            u.delete()
        except User.DoesNotExist:
            continue
        finally:
            print i
            i += 1
    block_ips(ips)


def spider_users(users):
    users = set(users)
    count = len(users)
    ips = get_ips_by_users(users)
    users |= get_users_by_ips(ips)
    if len(users) == count:
        return users
    return spider_users(users)


def get_ips_by_users(users):
    ips = set()
    for u in users:
        for pr in u.postrevisions.all():
            if pr.ip_addr != '0.0.0.0':
                ips.add(pr.ip_addr)
    return ips


def get_users_by_ips(ips):
    users = set()
    for pr in PostRevision.objects.filter(ip_addr__in=ips):
        users.add(pr.author)
    return users


def get_domains_by_users(users):
    domains = set()
    for u in users:
        if '@' in u.email:
            domains.add(u.email.split('@')[1])
    return domains


def get_user_info(users):
    blank_users = list()
    info = list()
    for u in users:
        if u.about:
            info.append((u.id, u.email, u.about[:80]))
        elif u.posts.count():
            info.append((u.id, u.email, u.posts.all()[0].text[:80]))
        else:
            blank_users.append(u)
    for u in blank_users:
        info.append((u.id, u.email, ''))
    return info


def print_info(info):
    for i in info:
        print i

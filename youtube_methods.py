from datetime import datetime, date

def getLikePercentage(likes, dislikes):
    total = likes + dislikes
    return (likes / total)

def getDislikePercentage(likes, dislikes):
    total = likes + dislikes
    return (dislikes / total)

def getReactionPercentage(view_count, likes, dislikes):
    total_reaction = likes + dislikes
    return (total_reaction / view_count)

def getViewsPerDay(view_count, published_date):
    views_per_day = round(view_count / getDaysPassedFromUploadDate(published_date))
    return views_per_day

def getLikesPerDay(likes, published_date):
    likes_per_day = round(likes / getDaysPassedFromUploadDate(published_date))
    return likes_per_day

def getDislikesPerDay(dislikes, published_date):
    dislikes_per_day = round(dislikes / getDaysPassedFromUploadDate(published_date))
    return dislikes_per_day

def getDaysPassedFromUploadDate(published_date):
    dt = datetime.strptime(published_date, "%Y-%m-%d %H:%M:%S")
    upload_date = date(dt.year, dt.month, dt.day)
    now = datetime.now()
    today = date(now.year, now.month, now.day)
    days_passed_from_upload_date = (today - upload_date).days + 1
    return days_passed_from_upload_date
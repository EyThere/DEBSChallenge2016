import pymongo
import collections
from datetime import timedelta

client = pymongo.MongoClient(connect=False)

db = client.debs_db

posts = db.posts
users = db.users
comments = db.comments
postDic = collections.defaultdict(dict)

posts.create_index([("totalScore", pymongo.DESCENDING), ("ts", pymongo.DESCENDING)])

''' update posts and comments score according to the time-
    reduce points as the number of days passed + update the ts

    bDbAccess - True if we want to use less accesses to the DB
    bDelete - True if we should delete inactive comments and posts
'''

def updateCurrentTime(currTime, bDbAccess, bDelete):
    global postDic
    flag_print = False
    oneDay = timedelta(days=1)
    outOfDatesComments = comments.find({'score': {'$gt': 0}, 'ts': {'$lte': (currTime - oneDay)}})

    if bDbAccess:
        outOfDatesPosts = posts.update({'score': {'$gt': 0}, 'ts': {'$lte': (currTime - oneDay)}},
                                       {'$set': {'ts': currTime}, '$inc': {'score': -1, 'totalScore': -1}},
                                       multi=True)
        if (outOfDatesPosts['nModified'] != 0):
            flag_print = True
    else:
        outOfDatesPosts = posts.find({"score": {'$gt': 0}, 'ts': {'$lte': (currTime - oneDay)}})
        for obj in outOfDatesPosts:
            flag_print = True
            posts.update({'_id': obj['_id']}, {'$set': {'ts': currTime}, '$inc': {"score": -1, "totalScore": -1}})

    for obj in outOfDatesComments:
        flag_print = True
        comments.update({'_id': obj['_id']}, {'$set': {'ts': currTime}, '$inc': {"score": -1}})
        posts.update({'_id': obj['post_id']}, {'$inc': {"totalScore": -1}})
        ''' If comment is no longer active, update post's commenterComments.
         No need to update comments_ts since we only use it for sort and we sort by decrease order'''
        if ( obj['score']-1 == 0 ):
            commenterComments = list(postDic[obj['post_id']][obj['user_id']])
            commenterComments.remove(obj['_id'])
            ''' If this commenters doesn't have amymore comments on this post, remove it from the post's commenters '''
            if commenterComments == []:
                postDic[obj['post_id']].pop(obj['user_id'], None)
            else:
                postDic[obj['post_id']][obj['user_id']] = commenterComments

    if bDelete:
        ''' remove all posts and comments that are no longer active '''
        posts.remove({ "totalScore": {'$eq': 0} })
        comments.remove({ "score": {'$eq': 0} })
    return flag_print

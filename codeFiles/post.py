from utils import posts, updateCurrentTime, postDic
from copy import copy


''' A global variable of the top 3 posts ids'''
globalTop3 = [0,0,0]
'''The way to update a nested dictionary:'''
# d['dict1']['innerkey'] = 'value'

def AddPost(ts, post_id, user_id, post_content, user_name):
    postDic[post_id] = {}
    post = {"_id": post_id,
            "ts": ts,
            "user_id": user_id,
            "user_name": user_name,
            "score": 10, # score of the post. never increase, only decrease
            "totalScore": 10, # total score - score above + comments scores
            "comments_ts": [] #should we index this field too?
            }
    posts.insert_one(post)
    return True


def AddCommentToPost(post_id, comment_ts, commenter_id, comment_id):
    posts.update({'_id': post_id, "score": {'$gt': 0 }},
                 {
                    '$push': {'comments_ts': comment_ts},
                   #'$addToSet': {'commenters_ids': commenter_id},
                    '$inc': {'totalScore': 10}
                 }
                )
    '''add to the relevant post's commenter list a new comment_id'''
    commenterComments = []
    if commenter_id not in postDic[post_id]:
        postDic[post_id][commenter_id] = {}
    commenterComments = list(postDic[post_id][commenter_id])
    commenterComments.append(comment_id)
    postDic[post_id][commenter_id] = commenterComments

def Top3Posts():
    global globalTop3
    top3 = posts.find({"totalScore": {'$gt': 0}},{"user_id": 0, "post":0,"comments_ts":0})\
            .sort([("totalScore", -1), ('ts', -1), ('comments_ts', -1),('_id',-1)]).limit(3)
    top3List = []
    top3Ids = []
    for top in top3:
        top['numOfCommenters'] = len(postDic[top['_id']])
        top3List.append(top)
        top3Ids.append(top['_id'])

    output = ""
    if top3Ids != globalTop3:
        for doc in top3List:
            output += ","+str(doc["_id"])
            output += ","+ str(doc["user_name"])
            output += ","+ str(doc["totalScore"])
            output += ","+ str(doc["numOfCommenters"])
        count = len(top3Ids)
        while (count != 3):
            output+= ",-,-,-,-"
            count+=1
        globalTop3 = copy(top3Ids)
    return output

''' Improve: check if the new post/comment has a bigger score than the third one in the top 3 '''
def checkNewTop(ts):
    global globalTop3
    result = Top3Posts()
    if result != "":
        result = ts.isoformat().replace('000','').replace('00:00','0000') + result
        return result
    return False

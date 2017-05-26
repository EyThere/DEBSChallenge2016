from utils import comments, updateCurrentTime
import post

def AddComment(ts, comment_id, user_id, comment_content, user_name, comment_replied, post_commented):
    #They say if -1 but in some inputs it is ''
    post_id_to_send = 0
    if comment_replied == '' or comment_replied=='-1':
        post_id_to_send = post_commented
    else:
        all = comments.find({'_id': comment_replied})
        for localPost in all:
            post_id_to_send = localPost['post_id']

    comment = {"ts": ts,
               "_id": comment_id,
               "user_id": user_id,
               "post_id": post_id_to_send,
               "score": 10
            }
    comments.insert_one(comment)
    post.AddCommentToPost(post_id_to_send,ts,user_id,comment_id)
    return True


import React, { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, MoreVertical, Reply } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { commentApi, authHelpers, handleApiError } from '../services/api';

const CommentSection = ({ videoId }) => {
  const [newComment, setNewComment] = useState('');
  const [showCommentInput, setShowCommentInput] = useState(false);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentUser] = useState(authHelpers.getCurrentUser());

  useEffect(() => {
    loadComments();
  }, [videoId]);

  const loadComments = async () => {
    if (!videoId) return;
    
    try {
      setLoading(true);
      const commentsData = await commentApi.getVideoComments(videoId, {
        limit: 50,
        include_replies: true
      });
      setComments(commentsData.comments || []);
    } catch (error) {
      console.error('Error loading comments:', handleApiError(error));
      setComments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async () => {
    if (newComment.trim() && currentUser) {
      try {
        const commentData = {
          content: newComment,
          video_id: videoId
        };
        
        const createdComment = await commentApi.createComment(commentData);
        
        // Add new comment to the top of the list
        setComments([createdComment, ...comments]);
        setNewComment('');
        setShowCommentInput(false);
      } catch (error) {
        console.error('Error creating comment:', handleApiError(error));
        alert('Failed to post comment. Please try again.');
      }
    }
  };

  const handleLikeComment = async (commentId) => {
    if (!currentUser) {
      alert('Please sign in to like comments');
      return;
    }

    try {
      await commentApi.likeComment(commentId);
      // Update the comment in the list
      setComments(comments.map(comment => 
        comment.id === commentId 
          ? { ...comment, metrics: { ...comment.metrics, likes: comment.metrics.likes + 1 }}
          : comment
      ));
    } catch (error) {
      console.error('Error liking comment:', handleApiError(error));
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="mt-8">
      <div className="flex items-center space-x-4 mb-6">
        <h3 className="text-lg font-semibold">{localComments.length} Comments</h3>
        <Button variant="ghost" size="sm" className="text-sm">
          Sort by
        </Button>
      </div>

      {/* Add Comment */}
      <div className="mb-8">
        <div className="flex space-x-3">
          <Avatar className="w-8 h-8">
            <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50&h=50&fit=crop&crop=face" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <Textarea
              placeholder="Add a comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              onFocus={() => setShowCommentInput(true)}
              className="min-h-0 resize-none border-0 border-b-2 border-gray-200 rounded-none px-0 py-2 focus:border-blue-500 transition-colors"
            />
            {showCommentInput && (
              <div className="flex items-center justify-end space-x-2 mt-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setShowCommentInput(false);
                    setNewComment('');
                  }}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSubmitComment}
                  disabled={!newComment.trim()}
                  className="rounded-full"
                >
                  Comment
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Comments List */}
      <div className="space-y-6">
        {localComments.map((comment) => (
          <div key={comment.id} className="flex space-x-3">
            <Avatar className="w-8 h-8 flex-shrink-0">
              <AvatarImage src={comment.authorAvatar} />
              <AvatarFallback>{comment.author[0]}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <span className="font-medium text-sm">{comment.author}</span>
                <span className="text-xs text-gray-500">{comment.timestamp}</span>
              </div>
              <p className="text-sm mb-2 leading-relaxed">{comment.content}</p>
              <div className="flex items-center space-x-4">
                <Button variant="ghost" size="sm" className="p-1 h-auto hover:bg-gray-100 rounded-full">
                  <ThumbsUp className="w-4 h-4 mr-1" />
                  <span className="text-xs">{comment.likes > 0 ? formatNumber(comment.likes) : ''}</span>
                </Button>
                <Button variant="ghost" size="sm" className="p-1 h-auto hover:bg-gray-100 rounded-full">
                  <ThumbsDown className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" className="text-xs hover:bg-gray-100 rounded-full">
                  <Reply className="w-3 h-3 mr-1" />
                  Reply
                </Button>
                <Button variant="ghost" size="sm" className="p-1 h-auto hover:bg-gray-100 rounded-full">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </div>

              {/* Replies */}
              {comment.replies && comment.replies.length > 0 && (
                <div className="mt-4 space-y-4">
                  {comment.replies.map((reply) => (
                    <div key={reply.id} className="flex space-x-3">
                      <Avatar className="w-6 h-6 flex-shrink-0">
                        <AvatarImage src={reply.authorAvatar} />
                        <AvatarFallback>{reply.author[0]}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-sm">{reply.author}</span>
                          <span className="text-xs text-gray-500">{reply.timestamp}</span>
                        </div>
                        <p className="text-sm mb-2 leading-relaxed">{reply.content}</p>
                        <div className="flex items-center space-x-4">
                          <Button variant="ghost" size="sm" className="p-1 h-auto hover:bg-gray-100 rounded-full">
                            <ThumbsUp className="w-3 h-3 mr-1" />
                            <span className="text-xs">{reply.likes > 0 ? formatNumber(reply.likes) : ''}</span>
                          </Button>
                          <Button variant="ghost" size="sm" className="p-1 h-auto hover:bg-gray-100 rounded-full">
                            <ThumbsDown className="w-3 h-3" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-xs hover:bg-gray-100 rounded-full">
                            Reply
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommentSection;
function hideAllLists(postId) {
    document.getElementById('likes-list-' + postId).classList.add('hidden');
    document.getElementById('comments-list-' + postId).classList.add('hidden');
}
function loadLikes(postId) {
    hideAllLists(postId);
    fetch(`/ajax/post-likes/${postId}/`)
        .then(response => {
            console.log('Likes response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Likes response data:', data);
            const container = document.getElementById('likes-list-' + postId);
            container.innerHTML = data.html + `<div class='mt-2'><button class='text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded hover:bg-gray-300 transition' onclick='hideAllLists(${postId})'>Hide</button></div>`;
            container.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error loading likes:', error);
        });
}
function loadComments(postId) {
    hideAllLists(postId);
    fetch(`/ajax/post-comments/${postId}/`)
        .then(response => {
            console.log('Comments response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Comments response data:', data);
            const container = document.getElementById('comments-list-' + postId);
            container.innerHTML = data.html + `<div class='mt-2'><button class='text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded hover:bg-gray-300 transition' onclick='hideAllLists(${postId})'>Hide</button></div>`;
            container.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error loading comments:', error);
        });
}
function showReplyForm(commentId) {
    document.getElementById('reply-form-' + commentId).classList.remove('hidden');
}
function hideReplyForm(commentId) {
    document.getElementById('reply-form-' + commentId).classList.add('hidden');
}
function submitReply(event, commentId, postId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input[name="reply_text"]');
    const replyText = input.value.trim();
    if (!replyText) return;
    fetch(`/add-reply/${commentId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `reply_text=${encodeURIComponent(replyText)}`
    })
    .then(response => response.json())
    .then(data => {
        // Update the comments list for this post
        loadComments(postId);
        hideReplyForm(commentId);
        input.value = '';
    });
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function likePost(postId) {
    fetch(`/like-post/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        const heart = document.getElementById(`post-like-heart-${postId}`);
        const count = document.getElementById(`post-like-count-${postId}`);
        if (data.liked) {
            heart.classList.add('text-red-500');
            heart.classList.remove('text-gray-400');
            heart.setAttribute('fill', 'currentColor');
        } else {
            heart.classList.remove('text-red-500');
            heart.classList.add('text-gray-400');
            heart.setAttribute('fill', 'none');
        }
        count.textContent = data.like_count;
    });
}

function likeComment(commentId) {
    fetch(`/like-comment/${commentId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        const heart = document.getElementById(`comment-like-heart-${commentId}`);
        const count = document.getElementById(`comment-like-count-${commentId}`);
        if (data.liked) {
            heart.classList.add('text-red-500');
            heart.classList.remove('text-gray-400');
            heart.setAttribute('fill', 'currentColor');
        } else {
            heart.classList.remove('text-red-500');
            heart.classList.add('text-gray-400');
            heart.setAttribute('fill', 'none');
        }
        count.textContent = data.like_count;
    });
}
function likeReply(replyId) {
    fetch(`/like-reply/${replyId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        const heart = document.getElementById(`reply-like-heart-${replyId}`);
        const count = document.getElementById(`reply-like-count-${replyId}`);
        if (data.liked) {
            heart.classList.add('text-red-500');
            heart.classList.remove('text-gray-400');
            heart.setAttribute('fill', 'currentColor');
        } else {
            heart.classList.remove('text-red-500');
            heart.classList.add('text-gray-400');
            heart.setAttribute('fill', 'none');
        }
        count.textContent = data.like_count;
    });
} 
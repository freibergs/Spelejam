from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from ..models import Chat, Message, User, Product, db
from datetime import datetime

chat = Blueprint('chat', __name__)

@chat.route('/chats')
@login_required
def chats():
    chats = Chat.query.filter(Chat.participants.any(id=current_user.id)).filter(Chat.messages.any()).all()
    return render_template('chat/chats.html', chats=chats)

@chat.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat_detail(chat_id):
    chat = Chat.query.get_or_404(chat_id)

    if current_user not in chat.participants:
        flash("You are not authorized to view this chat.", "danger")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            receiver = next(participant for participant in chat.participants if participant.id != current_user.id)
            
            message = Message(
                chat_id=chat.id,
                sender_id=current_user.id,
                receiver_id=receiver.id,
                content=content
            )
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('chat.chat_detail', chat_id=chat.id))

    unread_messages = Message.query.filter_by(chat_id=chat.id, is_read=False)\
                                   .filter(Message.sender_id != current_user.id).all()
    for message in unread_messages:
        message.is_read = True
    db.session.commit()

    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()

    return render_template('chat/chat_detail.html', chat=chat, messages=messages, product=chat.product)

@chat.route('/start_chat/<int:product_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def start_chat(product_id, user_id):
    if user_id == current_user.id:
        flash("You cannot start a chat with yourself.", "warning")
        return redirect(url_for('product.product_detail', product_id=product_id, slug=Product.query.get(product_id).slug))

    existing_chat = Chat.query.filter_by(product_id=product_id)\
                              .filter(Chat.participants.any(id=user_id))\
                              .filter(Chat.participants.any(id=current_user.id)).first()

    if existing_chat:
        return redirect(url_for('chat.chat_detail', chat_id=existing_chat.id))

    new_chat = Chat(product_id=product_id)
    
    current_user_obj = User.query.get(current_user.id)
    recipient_user_obj = User.query.get(user_id)
    new_chat.participants.append(current_user_obj)
    new_chat.participants.append(recipient_user_obj)
    
    db.session.add(new_chat)
    db.session.commit()
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                chat_id=new_chat.id,
                sender_id=current_user.id,
                receiver_id=user_id,
                content=content
            )
            db.session.add(message)
            db.session.commit()

    return redirect(url_for('chat.chat_detail', chat_id=new_chat.id))


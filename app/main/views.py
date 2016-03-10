# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, flash,\
	request,current_app
from . import main
from .forms import NewTagForm, NewCatForm, NewItemForm, NewBlogForm,\
	QueryItemForm
from .. import db
from ..models import Blog, Item, Tag, Category 
from random import randint

@main.route('/')
def index():
	fan_paras = Tag.query.filter_by(name=u'摘抄').first().items
	fan_para_length = len(fan_paras)
	fan_para = fan_paras[randint(0,fan_para_length-1)]
	return render_template('index.html',fan_para=fan_para)
	
@main.route('/daily',methods=['GET','POST'])
def daily():
	form = QueryItemForm()
	if form.validate_on_submit():
		items = Item.query.filter_by(name=form.item_name.data).order_by(Item.timestamp.desc()).all()
		return render_template('daily.html',items=items,form=form,categories = Category.query.all())
	page = request.args.get('page',1,type=int)
	pagination = Item.query.order_by(Item.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
	items = pagination.items
	return render_template('daily.html',title=u"日常",items=items,form=form,pagination=pagination,categories = Category.query.all())

@main.route('/new_tag',methods=['GET','POST'])
def new_tag():
	form = NewTagForm()
	if form.validate_on_submit():
		tag = Tag(name=form.name.data)
		db.session.add(tag)
		return redirect(url_for('main.daily'))
	return render_template('new_form.html',title= u'新建标签',form=form)
	
@main.route('/daily/item/<int:item_id>',methods=['GET','POST'])
def item(item_id):
	form = QueryItemForm()
	if form.validate_on_submit():
		items = Item.query.filter_by(name=form.item_name.data).order_by(Item.timestamp.desc()).all()
		return render_template('daily.html',items=items,form=form,categories=Category.query.all())
	items = Item.query.filter_by(id=item_id).all()
	return render_template('daily.html',title=u"日常",items=items,form=form,categories = Category.query.all())

@main.route('/daily/edit/<int:item_id>',methods=['GET','POST'])
def edit_item(item_id):
	item = Item.query.filter_by(id=item_id).first()
	form = NewItemForm()
	form.tag_id.choices = [(g.id, g.name) for g in \
		Tag.query.order_by('id')]
	if form.validate_on_submit():
		item.name=form.name.data
		item.text=form.text.data
		item.tag_id=form.tag_id.data
		item.flags=form.flag.data
		db.session.add(item)
		return redirect(url_for('main.item',item_id=item_id))
	form.name.data = item.name
	form.text.data = item.text
	form.tag_id.data = item.tag_id
	form.flag.data = item.flags
	return render_template('new_form.html',title=u'修改备忘',form=form)

@main.route('/daily/tag/<int:tag_id>')
def tag(tag_id):
	form = QueryItemForm()
	if form.validate_on_submit():
		items = Item.query.filter_by(name=form.item_name.data).order_by(Item.timestamp.desc()).all()
		return render_template('daily.html',items=items,form=form,categories=Category.query.all())
	items = Tag.query.filter_by(id=tag_id).first().items
	return render_template('daily.html',title=u"日常",items=items,form=form,categories = Category.query.all())

@main.route('/new_item',methods=['GET','POST'])
def new_item():
	form = NewItemForm()
	form.tag_id.choices = [(g.id, g.name) for g in \
		Tag.query.order_by('id')]
	if form.validate_on_submit():
		item = Item(name=form.name.data,text=form.text.data,flags=0,\
			tag_id=form.tag_id.data)
		db.session.add(item)
		return redirect(url_for('main.daily'))
	return render_template('new_form.html',title=u'新建备忘',form=form)

@main.route('/blogs/category/<int:cat_id>',methods=['GET','POST'])
def category(cat_id):
	categories = Category.query.all()
	page = request.args.get('page',1,type=int)
	if cat_id == 0:
		title=u'博客'
		pagination = Blog.query.order_by(Blog.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
	else:
		title=Category.query.filter_by(id=cat_id).first().name
		pagination = Blog.query.filter_by(category_id=cat_id).order_by(Blog.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
	blogs = pagination.items
	return render_template('blogs.html',blogs=blogs,pagination=pagination,categories=categories,title=title)

@main.route('/blogs/article/<int:blog_id>',methods=['GET','POST'])
def article(blog_id):
	categories = Category.query.all()
	blogs = Blog.query.filter_by(id=blog_id).all()
	return render_template('blogs.html',blogs=blogs,categories=categories,title=blogs[0].category.name,single=True)
	
@main.route('/blogs/new_cat',methods=['GET','POST'])
def new_cat():
	form = NewCatForm()
	if form.validate_on_submit():
		category = Category(name=form.name.data)
		db.session.add(category)
		return redirect(url_for('main.category',cat_id=0))
	return render_template('new_form.html',title=u'新建目录',form=form)
	
@main.route('/blogs/new_blog',methods=['GET','POST'])
def new_blog():
	form = NewBlogForm()
	form.cat_id.choices = [(g.id, g.name) for g in \
		Category.query.order_by('id')]
	if form.validate_on_submit():
		blog = Blog(title=form.title.data,text=form.text.data,\
			category_id=form.cat_id.data,tag=form.tag.data,\
			abstract=form.abstract.data)
		db.session.add(blog)
		return redirect(url_for('main.category',cat_id=form.cat_id.data))
	return render_template('new_form.html',title=u'新建博客',form=form)

@main.route('/blogs/edit/<int:blog_id>',methods=['GET','POST'])
def edit_blog(blog_id):
	blog = Blog.query.filter_by(id=blog_id).first()
	form = NewBlogForm()
	form.cat_id.choices = [(g.id, g.name) for g in \
		Category.query.order_by('id')]
	if form.validate_on_submit():
		blog.title=form.title.data
		blog.text=form.text.data
		blog.category_id=form.cat_id.data
		blog.tag=form.tag.data
		blog.abstract=form.abstract.data
		db.session.add(blog)
		return redirect(url_for('main.article',blog_id=blog_id))
	form.title.data=blog.title
	form.text.data=blog.text
	form.cat_id.data=blog.category_id
	form.tag.data=blog.tag
	form.abstract.data=blog.abstract
	return render_template('new_form.html',title=u'修改博客',form=form)




@main.route('/about')
def about():
	categories = Category.query.all()
	return render_template('about.html',title=u'关于',categories=categories)
	
	
	



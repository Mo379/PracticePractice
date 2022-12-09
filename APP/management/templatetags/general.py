import os
from django.conf import settings
from django import template
from django.urls import reverse
from content.util.GeneralUtil import TagGenerator
from content.models import Point
import markdown
from django.template import Context, Template, loader

register = template.Library()


@register.filter(name='p_unique_to_title')
def p_unique_to_title(p_unique_id):
    """Splits a string into a list using key"""
    point = Point.objects.get(p_unique_id=p_unique_id)
    title = point.p_content['details']['hidden']['0']['point_title']
    return title

@register.filter(name='split')
def split(value, key):
    """Splits a string into a list using key"""
    return value.split(key)


@register.filter(name='index')
def index(indexable, i):
    """ Return ith index of list"""
    return indexable[i]


@register.filter(name='list_to_string')
def list_to_string(indexable, key):
    """ Turn the list into a string """
    indexable = list(indexable)
    lista = []
    for i in indexable:
        lista.append(str(i))
    string = str(key).join(lista)
    return string


@register.filter(name='has_group')
def has_group(user, group_name):
    """ The user is in this group"""
    return user.groups.filter(name=group_name).exists()


@register.filter(name='field_name_to_label')
def field_name_to_label(value):
    if value.lower() == 'alevels':
        value = 'A-Level'
    value = value.replace('_', ' ')
    return value.title()


@register.filter(name='paper_year')
def paper_year(value):
    value = str('20')+str(value)
    return value


@register.filter(name='paper_month')
def paper_month(value):
    value = str(value)
    if value in ['01', '1', '12', '11']:
        value = 'January'
    if value in ['05', '5', '06', '6', '07', '7']:
        value = 'June'
    return value


@register.filter(name='has_many_groups')
def has_many_groups(user, group_list_str):
    """ The user is in all of these groups """
    groups = group_list_str.split(' ')
    reports = []
    for group_name in groups:
        status = user.groups.filter(name=group_name).exists()
        if status:
            reports.append(status)
        else:
            reports.append(status)
    if False in reports:
        return False
    else:
        return True


@register.filter(name='in_groups')
def in_groups(user, group_list_str):
    """ The user is at least in one of these groups"""
    groups = group_list_str.split(' ')
    reports = []
    for group_name in groups:
        status = user.groups.filter(name=group_name).exists()
        if status:
            reports.append(status)
        else:
            reports.append(status)
    if True in reports:
        return True
    else:
        return False


@register.filter(name='dict')
def dict(var):
    """ Return the description of the variable """
    return var.__dict__


@register.simple_tag
def definevar(val=None):
    """ Define this variable """
    return val


@register.filter(name='divide')
def divide(value, arg):
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name='ToMarkdown')
def ToMarkdown(content, point):
    # setup output
    html = ""
    # kw items in content
    details = content['details']
    # kw items in details
    hidden = details['hidden']
    description = details['description']
    # numbered items in hidden and description
    # hidden has only one numbered element containing two children
    point_title = hidden['0']['point_title']
    #html += markdown.markdown("### " + str(number) + ': ' +point_title)
    html += markdown.markdown("### " + point_title)
    hidden_content = hidden['0']['content']
    # the content element is numbered
    video_html = ''
    for item in range(len(hidden_content)):
        # to keep the order of the content
        item = str(item)
        if 'vid' in hidden_content[item]:
            video = hidden_content[item]['vid']
            vid_title = video['vid_title']
            vid_link = video['vid_link']
            if vid_link:
                context = {
                        'vid_unique': TagGenerator(),
                        'vid_title': vid_title,
                        'vid_link': vid_link
                    }
                template = loader.get_template('content/video_popup.html')
                content = template.render(context)
                video_html += content

    # the description has many numbered elements
    content_html = ''
    for item in range(len(description)):
        # to keep the order of the description
        item = str(item)
        # each item has a single child either text or img
        # the text element is direct access
        if 'text' in description[item]:
            text = description[item]['text']
            text = text.replace('\\', '\\\\')
            content_html += text
        # the image element is made of two parts, info and file name
        if 'img' in description[item]:
            img_element = description[item]['img']
            img_info = img_element['img_info']
            img_name = img_element['img_name']
            if img_name and img_info:
                point_dir = point.p_files_directory
                file_path = os.path.join(point_dir, img_name)
                context = {
                        'CDN': settings.CDN_URL,
                        'img_info': img_info,
                        'file_path': file_path,
                    }
                template = loader.get_template('content/image_main.html')
                content = template.render(context)
                content_html += content
    # convert markdown to html for display
    html = markdown.markdown(html, extensions=['tables','admonition'])
    content_html = markdown.markdown(content_html, extensions=['tables','admonition'])
    return html + video_html + content_html



@register.filter(name='ToMarkdownQuestion')
def ToMarkdownQuestion(content, question):
    # setup output
    html = ""
    # kw items in content
    details = content['details']
    # kw items in details
    question_parts = details['questions']
    answer_parts= details['answers']
    # Title
    # The question part is different from the answer part
    for item in range(len(question_parts)):
        # to keep the order of the description
        item = str(item)
        q_part = question_parts[item]
        q_part_name = q_part['q_part']
        q_part_content = q_part['content']
        q_part_mark = q_part['q_part_mark']
        #
        if q_part_name != 'head':
            html += markdown.markdown("##### " + f'{q_part_name})')
        for content_item in range(len(q_part_content)):
            content_item = str(content_item)
            # each item has a single child either text or img
            # the text element is direct access
            if 'text' in q_part_content[content_item]:
                text = q_part_content[content_item]['text']
                text = text.replace('\\', '\\\\')
                html += markdown.markdown(text)
            # the image element is made of two parts, info and file name
            if 'img' in q_part_content[content_item]:
                img_element = q_part_content[content_item]['img']
                img_info = img_element['img_info']
                img_name = img_element['img_name']
                if img_name:
                    question_dir = question.q_files_directory
                    file_path = os.path.join(question_dir, img_name)
                    context = {
                            'CDN': settings.CDN_URL,
                            'img_info': img_info,
                            'file_path': file_path,
                        }
                    template = loader.get_template('content/image_question.html')
                    content = template.render(context)
                    html += content
        if q_part_name != 'head':
            html += f'<p style="text-align:right;"> [{q_part_mark}] </p>';
    # convert markdown to html for display
    return html


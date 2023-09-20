import os
from django.conf import settings
from django import template
from django.urls import reverse
from content.util.GeneralUtil import TagGenerator
from content.models import Point, Question
import markdown
from django.template import Context, Template, loader
from PP2.utils import h_encode
import json

register = template.Library()

@register.filter(name='dbobjmeta')
def dbobjmeta(obj, attribute):
    meta = dict(obj._meta)
    return meta.get(attribute)

@register.filter(name='TagGenerator')
def Generator(x):
    """Returns the contract for the contribution"""
    return TagGenerator()

@register.filter(name='hashid')
def hashid(id):
    """Return the 8 value hash id"""
    return h_encode(id)


@register.filter(name='p_unique_to_title')
def p_unique_to_title(p_unique_id):
    """Splits a string into a list using key"""
    point = Point.objects.get(p_unique_id=p_unique_id)
    title = point.p_title
    return title

@register.filter(name='p_unique_to_id')
def p_unique_to_id(p_unique_id):
    """Returns the point id from the unique id"""
    point = Point.objects.get(p_unique_id=p_unique_id)
    return point.id

@register.filter(name='split')
def split(value, key):
    """Splits a string into a list using key"""
    return value.split(key)


@register.filter(name='index')
def index(indexable, i):
    """ Return ith index of list"""
    try:
        output = indexable[i]
        return output
    except Exception:
        return False


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


@register.filter(name='get_image_name')
def get_image_name(value):
    filename = value.split('_')[-1]  # Split the string by '/' and get the last element
    return filename


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


@register.filter(name='check_student_module_progress_content')
def check_student_module_progress_content(tracks, course_content):
    if tracks:
        for course_chapter in course_content.keys():
            if course_chapter not in tracks.keys():
                return False
            elif 'content' not in tracks[course_chapter].keys():
                return False
        return True
    else:
        return False


@register.filter(name='check_student_module_progress_questions')
def check_student_module_progress_questions(tracks, course_content):
    if tracks:
        for course_chapter in course_content.keys():
            if course_chapter not in tracks.keys():
                return False
            elif 'questions' not in tracks[course_chapter].keys():
                return False
        return True
    else:
        return False


@register.filter(name='get_percent')
def get_percent(denominator, numerator):
    return (denominator/numerator)*100


@register.filter(name='get_quiz_id')
def get_quiz_id(content):
    # setup output
    content = json.loads(content)
    return content['unique_id']
@register.filter(name='ToJson')
def ToJson(content):
    # setup output
    content = json.dumps(content)
    return content

@register.filter(name='GetMathString')
def GetMathString(content):
    # setup output
    content = content.replace('\\', '\\\\')
    return content
@register.filter(name='ProcessToMarkdown')
def ProcessToMarkdown(content):
    # setup output
    #content_html = markdown.markdown(content, extensions=['tables','admonition', 'fenced_code'])
    return content



@register.filter(name='ToMarkdown')
def ToMarkdown(content, point_id):
    # setup output
    html = ""
    # kw items in content
    point = Point.objects.get(pk=point_id)
    description = point.p_content
    point_title = point.p_title.replace('_', ' ').title()
    videos = point.p_videos.all()
    images = point.p_images.all()
    #
    html += markdown.markdown("### " + point_title)
    # the content element is numbered
    video_html = ''
    for vid in videos:
        vid_title = vid.title
        vid_link = vid.url
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
    if str(type(description)) == "<class 'dict'>":
        for item in range(len(description)):
            # to keep the order of the description
            item = str(item)
            # each item has a single child either text or img
            # the text element is direct access
            if 'text' in description[item]:
                text = str(description[item]['text'])
                text = text.replace('\\', '\\\\')
                content_html += text
            # the image element is made of two parts, info and file name
            if 'img' in description[item]:
                img_element = description[item]['img']
                img_info = img_element['img_info']
                img_name = img_element['img_name']
                if img_name and img_info:
                    file_path = os.path.join('universal/', f'point_{point.id}_{img_name}')
                    context = {
                            'CDN': settings.CDN_URL,
                            'img_info': img_info,
                            'file_path': file_path,
                        }
                    template = loader.get_template('content/image_main.html')
                    content = template.render(context)
                    content_html += content
    else:
        content_html += description
    # convert markdown to html for display
    html = markdown.markdown(html, extensions=['tables','admonition'])
    content_html = markdown.markdown(content_html, extensions=['tables','admonition'])
    return html + video_html + content_html



@register.filter(name='ToMarkdownManual')
def ToMarkdownManual(content, point_id):
    # setup output
    html = ""
    # kw items in content
    point = Point.objects.get(pk=point_id)
    description = point.p_content
    point_title = point.p_title.replace('_', ' ').title()
    videos = point.p_videos.all()
    images = point.p_images.all()
    #
    html += markdown.markdown("### " + point_title)
    # the content element is numbered
    video_html = ''
    script_html = ''
    video_tags = []
    for vid in videos:
        vid_title = vid.title
        vid_link = vid.url
        if vid_link:
            video_tag =  TagGenerator()
            video_tags.append(video_tag)
            context = {
                    'vid_unique': video_tag,
                    'vid_title': vid_title,
                    'vid_link': vid_link
                }
            template = loader.get_template('content/video_popup_manual.html')
            script_template = loader.get_template('content/video_popup_manual_script.html')
            content = template.render(context)
            script_content = script_template.render(context)
            video_html += content
            script_html += script_content

    # the description has many numbered elements
    content_html = ''
    if str(type(description)) == "<class 'dict'>":
        for item in range(len(description)):
            # to keep the order of the description
            item = str(item)
            # each item has a single child either text or img
            # the text element is direct access
            if 'text' in description[item]:
                text = str(description[item]['text'])
                text = text.replace('\\', '\\\\')
                content_html += text
            # the image element is made of two parts, info and file name
            if 'img' in description[item]:
                img_element = description[item]['img']
                img_info = img_element['img_info']
                img_name = img_element['img_name']
                if img_name and img_info:
                    file_path = os.path.join('universal/', f'point_{point.id}_{img_name}')
                    context = {
                            'CDN': settings.CDN_URL,
                            'img_info': img_info,
                            'file_path': file_path,
                        }
                    template = loader.get_template('content/image_main.html')
                    content = template.render(context)
                    content_html += content
    else:
        content_html += description
    # convert markdown to html for display
    html = markdown.markdown(html, extensions=['tables','admonition'])
    content_html = markdown.markdown(content_html, extensions=['tables','admonition'])
    return html + content_html, video_html, script_html, video_tags



@register.filter(name='ToMarkdownQuestion')
def ToMarkdownQuestion(content, question_id):
    # setup output
    # kw items in content
    question = Question.objects.get(pk=question_id)
    description = question.q_content
    videos = question.q_videos.all()
    images = question.q_images.all()
    #
    # the description has many numbered elements
    # the content element is numbered
    question_video_html = ''
    for vid in videos:
        vid_title = vid.title
        vid_link = vid.url
        if vid_link:
            context = {
                    'vid_unique': TagGenerator(),
                    'vid_title': vid_title,
                    'vid_link': vid_link
                }
            template = loader.get_template('content/video_popup.html')
            content = template.render(context)
            if vid.in_question_placement:
                question_video_html += content
    content_html = ''
    if str(type(description)) == "<class 'dict'>":
        for item in range(len(description)):
            # to keep the order of the description
            item = str(item)
            # each item has a single child either text or img
            # the text element is direct access
            if 'text' in description[item]:
                text = str(description[item]['text'])
                text = text.replace('\\', '\\\\')
                content_html += text
            # the image element is made of two parts, info and file name
            if 'img' in description[item]:
                img_element = description[item]['img']
                img_info = img_element['img_info']
                img_name = img_element['img_name']
                if img_name and img_info:
                    file_path = os.path.join('universal/', f'question_{question.id}_{img_name}')
                    context = {
                            'CDN': settings.CDN_URL,
                            'img_info': img_info,
                            'file_path': file_path,
                        }
                    template = loader.get_template('content/image_main.html')
                    content = template.render(context)
                    content_html += content
    else:
        content_html += description
    content_html = markdown.markdown(content_html, extensions=['tables','admonition'])
    return question_video_html + content_html


@register.filter(name='ToMarkdownAnswer')
def ToMarkdownAnswer(content, question_id):
    # setup output
    # kw items in content
    question = Question.objects.get(pk=question_id)
    description = question.q_answer
    videos = question.q_videos.all()
    images = question.q_images.all()
    #
    # the description has many numbered elements
    # the content element is numbered
    answer_video_html = ''
    for vid in videos:
        vid_title = vid.title
        vid_link = vid.url
        if vid_link:
            context = {
                    'vid_unique': TagGenerator(),
                    'vid_title': vid_title,
                    'vid_link': vid_link
                }
            template = loader.get_template('content/video_popup.html')
            content = template.render(context)
            if vid.in_question_placement == False:
                answer_video_html += content
    content_html = ''
    if str(type(description)) == "<class 'dict'>":
        for item in range(len(description)):
            # to keep the order of the description
            item = str(item)
            # each item has a single child either text or img
            # the text element is direct access
            if 'text' in description[item]:
                text = str(description[item]['text'])
                text = text.replace('\\', '\\\\')
                content_html += text
            # the image element is made of two parts, info and file name
            if 'img' in description[item]:
                img_element = description[item]['img']
                img_info = img_element['img_info']
                img_name = img_element['img_name']
                if img_name and img_info:
                    file_path = os.path.join('universal/', f'question_{question.id}_{img_name}')
                    context = {
                            'CDN': settings.CDN_URL,
                            'img_info': img_info,
                            'file_path': file_path,
                        }
                    template = loader.get_template('content/image_main.html')
                    content = template.render(context)
                    content_html += content
    else:
        content_html += description
    content_html = markdown.markdown(content_html, extensions=['tables','admonition'])
    return answer_video_html + content_html

@register.filter(name='ToMarkdownAnswerManual')
def ToMarkdownAnswerManual(content, question_id):
    # setup output
    # kw items in content
    question = Question.objects.get(pk=question_id)
    description = question.q_answer
    videos = question.q_videos.all()
    images = question.q_images.all()
    #
    # the description has many numbered elements
    # the content element is numbered
    video_html = ''
    script_html = ''
    video_tags = []
    for vid in videos:
        vid_title = vid.title
        vid_link = vid.url
        if vid_link:
            video_tag = TagGenerator()
            video_tags.append(video_tag)
            context = {
                    'vid_unique': video_tag,
                    'vid_title': vid_title,
                    'vid_link': vid_link
                }
            template = loader.get_template('content/video_popup_manual.html')
            script_template = loader.get_template('content/video_popup_manual_script.html')
            content = template.render(context)
            script_content = script_template.render(context)
            video_html += content
            script_html += script_content

    # the description has many numbered elements
    content_html = ''
    if str(type(description)) == "<class 'dict'>":
        for item in range(len(description)):
            # to keep the order of the description
            item = str(item)
            # each item has a single child either text or img
            # the text element is direct access
            if 'text' in description[item]:
                text = str(description[item]['text'])
                text = text.replace('\\', '\\\\')
                content_html += text
            # the image element is made of two parts, info and file name
            if 'img' in description[item]:
                img_element = description[item]['img']
                img_info = img_element['img_info']
                img_name = img_element['img_name']
                if img_name and img_info:
                    file_path = os.path.join('universal/', f'question_{question.id}_{img_name}')
                    context = {
                            'CDN': settings.CDN_URL,
                            'img_info': img_info,
                            'file_path': file_path,
                        }
                    template = loader.get_template('content/image_main.html')
                    content = template.render(context)
                    content_html += content
    else:
        content_html += description
    content_html = markdown.markdown(content_html, extensions=['tables','admonition'])
    return content_html, video_html, script_html, video_tags

@register.filter(name='DifficultyToLabel')
def DifficultyToLabel(diff):
    """ Return the label of the difficulty """
    diff = int(diff) - 1
    labels = ['Basic', 'Easy', 'Medium', 'Hard', 'Very Hard']
    icons = ['<i class="bi bi-snow2"></i>','<i class="bi bi-reception-2"></i>','<i class="bi bi-reception-3"></i>','<i class="bi bi-reception-4"></i>','<i class="bi bi-radioactive"></i>']
    label = icons[diff] + ' ' + labels[diff]
    return label


@register.filter(name='QuestionMarkRange')
def filter_range(start, end):
    return range(start, end+1)


@register.filter(name='group_chat_thread')
def group_chat_thread(array):
    """Takes the group chat thread and groups it into user assistant response pairts"""
    def divide_chunks(array, n):
        # looping till length l
        for i in range(0, len(array), n):
            yield array[i:i + n]
    #
    grouped_threads = list(divide_chunks(array, 2))
    return grouped_threads


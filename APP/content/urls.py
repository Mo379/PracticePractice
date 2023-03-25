from django.urls import path
from content import views


# App name
app_name = 'content'
urlpatterns = [
    path('content/', views.ContentView.as_view(), name='content'),
    path('content/<int:page>', views.ContentView.as_view(), name='content'),
    path(
        'content/questionbank/<hashid:course_id>/',
        views.QuestionBankView.as_view(),
        name='questionbank'
        ),
    path(
        'content/customtest/<hashid:paper_id>/',
        views.CustomTestView.as_view(),
        name='customtest'
        ),
    path(
        'content/practice/<hashid:course_id>/<module>/<chapter>/',
        views.PracticeView.as_view(),
        name='practice'
        ),
    path('content/notes/<hashid:course_id>', views.NotesView.as_view(), name='notes'),
    path(
        'content/note-article/<hashid:course_id>/<module>/<chapter>/',
        views.NoteArticleView.as_view(),
        name='notearticle'
    ),
    path(
        'content/noteedit/<hashid:spec_id>/<module>/<chapter>/',
        views.NoteEditView.as_view(),
        name='noteedit'
    ),
    path(
        'content/questionedit/<hashid:spec_id>/<module>/<chapter>/',
        views.QuestionEditView.as_view(),
        name='questionedit'
        ),
    path(
        'content/editorpoint/<hashid:spec_id>/<hashid:point_id>',
        views.EditorPointView.as_view(),
        name='editorpoint'
    ),
    path(
        'content/editorquestion/<hashid:spec_id>/<hashid:question_id>',
        views.EditorQuestionView.as_view(),
        name='editorquestion'
    ),
    #
    path(
        'content/contribution_noteedit/<hashid:task_id>',
        views.ContributionNoteEditView.as_view(),
        name='contribution_noteedit'
    ),
    path(
        'content/contribution_questionedit/<hashid:task_id>',
        views.ContributionQuestionEditView.as_view(),
        name='contribution_questionedit'
        ),
    path(
        'content/contribution_editorpoint/<hashid:task_id>/<hashid:point_id>',
        views.ContributionEditorPointView.as_view(),
        name='contribution_editorpoint'
    ),
    path(
        'content/contribution_editorquestion/<hashid:task_id>/<hashid:question_id>',
        views.ContributionEditorQuestionView.as_view(),
        name='contribution_editorquestion'
    ),
    #
    path(
        'content/_inheritfromspec',
        views._inheritfromspec,
        name='_inheritfromspec'
    ),
    path(
        'content/_add_collaborator',
        views._add_collaborator,
        name='_add_collaborator'
    ),
    path(
        'content/_assign_collaborator_spec',
        views._assign_collaborator_spec,
        name='_assign_collaborator_spec'
    ),
    path(
        'content/_ordermoduels',
        views._ordermoduels,
        name='_ordermoduels'
    ),
    path(
        'content/_orderchapters',
        views._orderchapters,
        name='_orderchapters'
    ),
    path(
        'content/_ordertopics',
        views._ordertopics,
        name='_ordertopics'
    ),
    path(
        'content/_orderpoints',
        views._orderpoints,
        name='_orderpoints'
    ),
    path(
        'content/_createcourse/',
        views._createcourse,
        name='_createcourse'
    ),
    path(
        'content/_deletecourse/',
        views._deletecourse,
        name='_deletecourse'
    ),
    path(
        'content/_updatecourseinformation/',
        views._updatecourseinformation,
        name='_updatecourseinformation'
    ),
    path(
        'content/_createversion/',
        views._createversion,
        name='_createversion'
    ),
    path(
        'content/_publishcourse/',
        views._publishcourse,
        name='_publishcourse'
    ),
    path(
        'content/_unpublishcourse/',
        views._unpublishcourse,
        name='_unpublishcourse'
    ),
    path(
        'content/_course_subscribe/',
        views._course_subscribe,
        name='_course_subscribe'
    ),
    path(
        'content/_createspec/',
        views._createspec,
        name='_createspec'
    ),
    path(
        'content/_deletespec/',
        views._deletespec,
        name='_deletespec'
    ),
    path(
        'content/_renamespec/',
        views._renamespec,
        name='_renamespec'
    ),
    path(
        'content/_createmoduel/',
        views._createmoduel,
        name='_createmoduel'
    ),
    path(
        'content/_deletemoduel/',
        views._deletemoduel,
        name='_deletemoduel'
    ),
    path(
        'content/_renamemodule/',
        views._renamemodule,
        name='_renamemodule'
    ),
    path(
        'content/_createchapter/',
        views._createchapter,
        name='_createchapter'
    ),
    path(
        'content/_deletechpter/',
        views._deletechapter,
        name='_deletechapter'
    ),
    path(
        'content/_renamechapter/',
        views._renamechapter,
        name='_renamechapter'
    ),
    path(
        'content/_createtopic/',
        views._createtopic,
        name='_createtopic'
    ),
    path(
        'content/_deletetopic/',
        views._deletetopic,
        name='_deletetopic'
    ),
    path(
        'content/_renametopic/',
        views._renametopic,
        name='_renametopic'
    ),
    path(
        'content/_createpoint/',
        views._createpoint,
        name='_createpoint'
    ),
    path(
        'content/_deletepoint/',
        views._deletepoint,
        name='_deletepoint'
    ),
    path(
        'content/_savepointedit/',
        views._savepointedit,
        name='_savepointedit'
    ),
    path(
        'content/_savequestionedit/',
        views._savequestionedit,
        name='_savequestionedit'
    ),
    path(
        'content/_contribution_savepointedit/',
        views._contribution_savepointedit,
        name='_contribution_savepointedit'
    ),
    path(
        'content/_contribution_savequestionedit/',
        views._contribution_savequestionedit,
        name='_contribution_savequestionedit'
    ),
    path(
        'content/_createcustomtest/',
        views._createcustomtest,
        name='_createcustomtest'
    ),
    # Management actions
    path(
        'content/_management_options/',
        views._management_options,
        name='_management_options'
    ),
    # Collaboration management actions
    path(
        'content/_collab_freelancer_conditions/',
        views._collab_freelancer_conditions,
        name='_collab_freelancer_conditions'
    ),
    path(
        'content/_collab_partner_conditions/',
        views._collab_partner_conditions,
        name='_collab_partner_conditions'
    ),
    path(
        'content/_condition_acceptance/',
        views._condition_acceptance,
        name='_condition_acceptance'
    ),
    path(
        'content/_initial_invitation_acceptance/',
        views._initial_invitation_acceptance,
        name='_initial_invitation_acceptance'
    ),
    path(
        'content/_start_new_task/',
        views._start_new_task,
        name='_start_new_task'
    ),
]

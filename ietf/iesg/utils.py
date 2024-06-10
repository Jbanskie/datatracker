from collections import namedtuple

import debug                            # pyflakes:ignore

from ietf.doc.models import Document, STATUSCHANGE_RELATIONS
from ietf.doc.utils_search import fill_in_telechat_date
from ietf.iesg.agenda import get_doc_section


TelechatPageCount = namedtuple('TelechatPageCount',['for_approval','for_action','related','ad_pages_left_to_ballot_on'])

def telechat_page_count(date=None, docs=None, ad=None):
    if not date and not docs:
        return TelechatPageCount(0, 0, 0, 0)

    if not docs:
        candidates = Document.objects.filter(docevent__telechatdocevent__telechat_date=date).distinct() 
        fill_in_telechat_date(candidates)
        docs = [ doc for doc in candidates if doc.telechat_date()==date ]

    for_action =[d for d in docs if get_doc_section(d).endswith('.3')]

    for_approval = set(docs)-set(for_action)

    drafts = [d for d in for_approval if d.type_id == 'draft']

    pages_for_approval = sum([d.pages or 0 for d in drafts])

    # from ballot_icon
    def sort_positions(t):
        _, pos = t
        if not pos:
            return (2, 0)
        elif pos.pos.blocking:
            return (0, pos.pos.order)
        else:
            return (1, pos.pos.order)

    ad_pages_left_to_ballot_on = None
    if ad:
        ad_pages_left_to_ballot_on = 0
        for doc in docs:
            ballot = doc.ballot if hasattr(doc, 'ballot') else doc.active_ballot()
            if ballot:
                positions = list(ballot.active_balloter_positions().items())
                positions.sort(key=sort_positions)
                ad_positions = list(filter(lambda position: position[0] == ad, positions))
                if len(ad_positions) == 0:
                    ad_pages_left_to_ballot_on += doc.pages or 0
                else:
                    latest_ad_position = ad_positions[0]
                    ballot_event = latest_ad_position[1]
                    if ballot_event: #FIXME: only count pages AD hasn't balloted on
                        ad_pages_left_to_ballot_on += doc.pages or 0

    pages_for_action = 0
    for d in for_action:
        if d.type_id == 'draft':
            pages_for_action += d.pages or 0
        elif d.type_id == 'statchg':
            for rel in d.related_that_doc(STATUSCHANGE_RELATIONS):
                pages_for_action += rel.pages or 0
        elif d.type_id == 'conflrev':
            for rel in d.related_that_doc('conflrev'):
                pages_for_action += rel.pages or 0
        else:
            pass

    related_pages = 0
    for d in for_approval-set(drafts):
        if d.type_id == 'statchg':
            for rel in d.related_that_doc(STATUSCHANGE_RELATIONS):
                related_pages += rel.pages or 0
        elif d.type_id == 'conflrev':
            for rel in d.related_that_doc('conflrev'):
                related_pages += rel.pages or 0
        else:
            # There's really nothing to rely on to give a reading load estimate for charters
            pass
    
    return TelechatPageCount(for_approval=pages_for_approval,
                             for_action=pages_for_action,
                             related=related_pages,
                             ad_pages_left_to_ballot_on=ad_pages_left_to_ballot_on)

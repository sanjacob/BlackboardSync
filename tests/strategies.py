from datetime import timezone

from pydantic import BaseModel
from hypothesis import given, infer
from hypothesis import strategies as st
from hypothesis.strategies import composite, DrawFn

from blackboard_sync.blackboard import (
    BBLocale, BBDuration, BBEnrollment, BBProctoring, BBFile, BBAttachment,
    BBCourseContent, BBAvailability)


handled_resource_types = ('x-bb-folder', 'x-bb-file', 'x-bb-document', 'x-bb-externallink')
unhandled_resource_types = ('x-bb-blankpage', 'x-bb-courselink', 'x-bb-syllabus', 'x-bb-toollink',
                            'x-bb-assignment', 'x-turnitin-assignment', 'x-bb-asmt-test-link',
                            'x-bb-bltiplacement-Portal', 'x-bb-bltiplacement-mediasite.lesopnames')
resource_types = handled_resource_types + unhandled_resource_types

class BlackboardCourseName(BaseModel):
    code: str
    title: str
    details: str

    @property
    def name(self):
        return f"{self.code} : {self.title}, {self.details}"


@composite
def bb_unhandled_resource_type(draw: DrawFn) -> str:
    res_type = draw(st.sampled_from(unhandled_resource_types))
    return f"resource/{res_type}"


@composite
def bb_handled_resource_type(draw: DrawFn) -> str:
    res_type = draw(st.sampled_from(handled_resource_types))
    return f"resource/{res_type}"


@composite
def bb_resource_type(draw: DrawFn) -> str:
    res_type = draw(st.sampled_from(resource_types))
    return f"resource/{res_type}"


@composite
def bb_course_code(draw: DrawFn) -> BlackboardCourseName:
    return draw(st.builds(BlackboardCourseName,
                          code=st.text().filter(lambda x: ':' not in x),
                          title=st.text().filter(lambda x: ',' not in x)))


st.register_type_strategy(BBLocale, st.builds(BBLocale, force=infer))
st.register_type_strategy(BBDuration, st.builds(BBDuration, type=infer))
st.register_type_strategy(BBEnrollment, st.builds(BBEnrollment, type=infer))
st.register_type_strategy(BBProctoring, st.builds(BBProctoring,
                                                  secureBrowserRequiredToTake=infer,
                                                  secureBrowserRequiredToReview=infer,
                                                  webcamRequired=infer))


@composite
def bb_proctorings(draw: DrawFn) -> BBProctoring:
    """Strategy to generate Blackboard Proctorings."""
    return draw()


@composite
def bb_file(draw: DrawFn) -> BBFile:
    """Strategy to generate Blackboard Files."""
    return draw(st.builds(BBFile, fileName=infer))


@composite
def bb_attachment(draw: DrawFn) -> BBAttachment:
    """Strategy to generate Blackboard Attachments"""
    return draw(st.builds(BBAttachment, id=infer, fileName=infer, mimeType=infer))


@composite
def bb_course_contents(draw: DrawFn) -> BBCourseContent:
    """A strategy to generate Blackboard Course Contents."""

    utc_strategy = st.just(timezone.utc)
    iso_datetime_strategy = st.datetimes(timezones=utc_strategy).map(lambda dt: dt.isoformat())

    draw(st.builds(BBCourseContent, id=infer, title=infer, body=infer,
                   created=iso_datetime_strategy, modified=iso_datetime_strategy,
                   position=infer, hasChildren=..., launchInNewWindow=infer,
                   reviewable=infer, availability=..., contentHandler=...,
                   links=..., hasGradebookColumns=infer, hasAssociatedGroups=infer))
    return 1


@composite
def bb_availabilities(draw: DrawFn) -> BBAvailability:
    """A strategy to generate Blackboard Availabities."""
    return draw(st.builds(BBAvailability, available="Yes"))

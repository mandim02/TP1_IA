from optapy import constraint_provider
from optapy.score import HardSoftScore
from optapy.constraint import ConstraintFactory, Joiners
from domain import Lesson
from datetime import datetime, date, timedelta


# 1 Sala por turma ao mesmo tempo
def room_conflict(constraint_factory: ConstraintFactory):
    # A room can accommodate at most one lesson_count at the same time.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              # ... in the same timeslot ...
              Joiners.equal(lambda lesson: lesson.timeslot),
              # ... in the same room ...
              # TODO: Pode estar mal
              filter(lambda room: room != "online", Joiners.equal(lambda lesson: lesson.room)),
              # form unique pairs
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .penalize("Room conflict", HardSoftScore.ONE_HARD)


# 1 professor por turma ao mesmo tempo
def teacher_conflict(constraint_factory: ConstraintFactory):
    # A teacher can teach at most one lesson_count at the same time.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.timeslot),
              Joiners.equal(lambda lesson: lesson.teacher),
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .penalize("Teacher conflict", HardSoftScore.ONE_HARD)


def student_group_conflict(constraint_factory: ConstraintFactory):
    # A student can attend at most one lesson_count at the same time.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.timeslot),
              Joiners.equal(lambda lesson: lesson.student_group),
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .penalize("Student group conflict", HardSoftScore.ONE_HARD)


def lesson_count(lessons, lesson):
    lessons[lesson.room.id] = lessons.get(lesson.room.id, 0) + 1
    return lesson


def lesson_count_OK(lessons, lesson):

    if lessons[lesson.room.id] > 4:
        return False
    elif lessons[lesson.room.id] >= 2:
        return True
    return False


# Cada turma tem 2 a 4 aulas numa sala especifica
def student_group_lesson_per_room_conflict(constraint_factory: ConstraintFactory):
    lessons = {}

    return constraint_factory\
        .for_each(Lesson)\
        .filter(lambda lesson1, lesson2: lesson1.student_group == lesson2.student_group)\
        .map(lambda lesson: lesson_count(lessons, lesson)) \
        .filter(lambda lesson: lesson_count_OK(lessons, lesson))\
        .reward("No conflict", HardSoftScore.ONE_HARD)


def lesson_count_dow(lessons, lesson):
    lessons[lesson.timeslot.day_of_week] = lessons.get(lesson.timeslot.day_of_week, 0) + 1
    return lesson


def student_group_three_lesson_per_day_conflict(constraint_factory: ConstraintFactory):
    lessons = {}

    return constraint_factory \
        .for_each(Lesson) \
        .filter(lambda lesson1, lesson2: lesson1.student_group == lesson2.student_group)\
        .filter(lambda lesson: lesson_count_dow(lessons, lesson))


# Informal Definition of Timetable Correctness

The set of group assigments to time slots and room(s) (timetable) for a given *Query* is correct if all of the below points are met:

* The capacity of each room in which a given group's classes are held is sufficient to accommodate the entire group
* Each group has assigned proper amount of rooms
* Each group has rooms assigned so that each element of the group's *labels* field is satisfied by some room
* Each group meets at times (starting slot and all subsequent slots based on the class duration) consistent with the group's availability
* Each group meets at times consistent with the availability of each assigned lecturer
* Each group meets at times consistent with the availability of each assigned room
* No lecturer teaches more than one group at a time
* No room is occupied by more than one group at a time
* All groups within a cluster meet in the blocks described by that cluster
#!/usr/bin/env python3
import aws_cdk as cdk

from cdk_habit_tracker.cdk_habit_tracker_stack import CdkHabitTrackerStack

app = cdk.App()
my_stack = CdkHabitTrackerStack(app, "CdkHabits",
    env={'region': 'us-east-1'}
)

app.synth()

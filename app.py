#!/usr/bin/env python3
import os
import jsii

import aws_cdk as cdk

from aws_cdk import (
    Aspects,
    CfnResource
)

@jsii.implements(cdk.IAspect)
class ForceDeletion:
    def visit(self, scope):
        if isinstance(scope, CfnResource):
            scope.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

from cdk_habit_tracker.cdk_habit_tracker_stack import CdkHabitTrackerStack


app = cdk.App()
my_stack = CdkHabitTrackerStack(app, "CdkHabits")
Aspects.of(my_stack).add(ForceDeletion())

app.synth()

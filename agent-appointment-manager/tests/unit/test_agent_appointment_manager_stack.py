import aws_cdk as core
import aws_cdk.assertions as assertions

from agent_appointment_manager.agent_appointment_manager_stack import AgentAppointmentManagerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in agent_appointment_manager/agent_appointment_manager_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AgentAppointmentManagerStack(app, "agent-appointment-manager")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

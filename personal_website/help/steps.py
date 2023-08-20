from .models import Procedure, ProcedureStep, ProcedureSubstep


def generate_default_procedure(user):
    # 为用户创建默认流程
    procedure = Procedure(name='工程外包流程（平台提供）', owner=user)
    procedure.save()
    steps = [
        ProcedureStep(procedure=procedure, title='明确需求', discription='双方合作完成需求清单，并提交给平台', pay=0),
        ProcedureStep(procedure=procedure, title='支付押金', discription='双方均向平台支付押金', pay=0),
        ProcedureStep(procedure=procedure, title='验收', discription='需方验收满意则需付款，不满意可取消合作', pay=100),
        ProcedureStep(procedure=procedure, title='部署', discription='部署完成后，竞方将收到平台托管的付款金额', pay=0),
        ProcedureStep(procedure=procedure, title='返还押金', discription='如果某方在验收时取消合作，则该方的押金不予退还', pay=0),
    ]
    for step in steps:
        step.save()
    ProcedureSubstep(step=steps[0], type=0, content="对方提交需求文档后，需要您进行审阅").save()
    ProcedureSubstep(step=steps[0], type=0, content="如果您对需求文档满意，则可点击“审阅通过”").save()

    ProcedureSubstep(step=steps[0], type=1, content="请您明确需求，并在输入框内撰写需求文档").save()
    ProcedureSubstep(step=steps[0], type=1, content="提交完成后，请主动联系对方进行核对").save()
    ProcedureSubstep(step=steps[0], type=1, content="一旦对方通过审核，将自动进入下一环节").save()




    ProcedureSubstep(step=steps[1], type=0, content="双方均向平台支付 10% 竞拍价作为押金").save()
    ProcedureSubstep(step=steps[1], type=0, content="如果一方在步骤 3，4 中主动取消合作，则会扣除该方的押金").save()

    ProcedureSubstep(step=steps[1], type=1, content="双方均向平台支付 10% 竞拍价作为押金").save()
    ProcedureSubstep(step=steps[1], type=1, content="如果一方在步骤 3，4 中主动取消合作，则会扣除该方的押金").save()
    ProcedureSubstep(step=steps[1], type=1, content="对方后续的付款也会转交至您支付押金的账户").save()




    ProcedureSubstep(step=steps[2], type=0, content="请等待对方联系您，使用“远程桌面”验收（右下角🎥）").save()
    ProcedureSubstep(step=steps[2], type=0, content="验收满意后请点击下方“我要付款”全额支付").save()
    ProcedureSubstep(step=steps[2], type=0, content="支付的金额由平台托管，待项目部署完成后转移至对方账户").save()

    ProcedureSubstep(step=steps[2], type=1, content="完成后请主动联系对方，使用“远程桌面”进行验收（右下角🎥）").save()
    ProcedureSubstep(step=steps[2], type=1, content="为了您的权益，在验收时不要将项目文件发送给对方").save()



    ProcedureSubstep(step=steps[3], type=0, content="请等待对方主动联系您进行部署").save()
    ProcedureSubstep(step=steps[3], type=0, content="平台提供了“发送文件”和“远程桌面”协助您的部署（右下角📎、🎥）").save()
    ProcedureSubstep(step=steps[3], type=0, content="部署完成后，请点击下方“已完成部署”").save()
    ProcedureSubstep(step=steps[3], type=0, content="点击“已完成部署”后，您支付的金额将转交至对方账户").save()

    ProcedureSubstep(step=steps[3], type=1, content="请您主动联系对方进行部署").save()
    ProcedureSubstep(step=steps[3], type=1, content="平台提供了“发送文件”和“远程桌面”协助您的部署（右下角📎、🎥）").save()
    ProcedureSubstep(step=steps[3], type=1, content="完成部署后，平台托管的金额在 3 个工作日内转移至您的账户").save()




    ProcedureSubstep(step=steps[4], type=0, content="请您完成对本次合作的评价").save()
    ProcedureSubstep(step=steps[4], type=0, content="评价完成后，您将在 3 个工作日内收到退还的押金").save()
    
    ProcedureSubstep(step=steps[4], type=1, content="请您完成对本次合作的评价").save()
    ProcedureSubstep(step=steps[4], type=1, content="评价完成后，您将在 3 个工作日内收到退还的押金").save()


    # procedure = Procedure(name='作业指导流程（平台提供）', owner=user)
    # procedure.save()
    # steps = [
    #     ProcedureStep(procedure=procedure, title='确认需求', discription='双方确认详细需求清单，并提交给平台', pay=0),
    #     ProcedureStep(procedure=procedure, title='服务商完成作业', discription='实现作业要求的各项功能', pay=0),
    #     ProcedureStep(procedure=procedure, title='作业验收合格', discription='查看完成的作业是否符合要求，不满意则无需支付并终止服务', pay=30),
    #     ProcedureStep(procedure=procedure, title='服务商讲解', discription='针对作业实现细节进行辅导讲解', pay=0),
    #     ProcedureStep(procedure=procedure, title='讲解完毕', discription='讲解满意再支付剩余70%的费用', pay=70),
    # ]
    # for step in steps:
    #     step.save()


    # procedure = Procedure(name='科研指导流程（平台提供）', owner=user)
    # procedure.save()
    # steps = [
    #     ProcedureStep(procedure=procedure, title='确认需求', discription='双方确认详细需求清单，并提交给平台', pay=0),
    #     ProcedureStep(procedure=procedure, title='服务商发掘创新点并进行实验', discription='阅读大量文献，寻找论文创新点，并在平台实时更新研究进度', pay=0),
    #     ProcedureStep(procedure=procedure, title='实验结果验收', discription='若验收满意需要支付30%费用，不满意则无需支付并终止服务', pay=30),
    #     ProcedureStep(procedure=procedure, title='服务商讲解实验细节', discription='针对实验细节进行辅导讲解', pay=0),
    #     ProcedureStep(procedure=procedure, title='讲解完毕', discription='讲解满意再支付剩余70%的费用', pay=70),
    # ]
    # for step in steps:
    #     step.save()
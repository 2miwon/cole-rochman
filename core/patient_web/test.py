for i in range(1,8):
        dailyresult=MedicationResult.objects.filter(patient__code__contains=request.user.username, date=cal_start_end_day(d, i))
        for r in dailyresult:
            #medication_time_num == 1:
            if r.status=="SUCCESS":
                mdresult[r.medication_time_num-1][i-1]="복약 성공"
            elif r.status=='DELAYED_SUCCESS':
                mdresult[r.medication_time_num - 1][i - 1] = "성공(지연)"
            elif r.status=='NO_RESPONSE':
                mdresult[r.medication_time_num - 1][i - 1] = "응답 없음"
            elif r.status=='FAILED':
                mdresult[r.medication_time_num - 1][i - 1] = "복약 실패"
            elif r.status=='SIDE_EFFECT':
                mdresult[r.medication_time_num - 1][i - 1] = "부작용"

    context['mdresult']=mdresult
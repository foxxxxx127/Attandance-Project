import {createRouter,createWebHistory} from 'vue-router'
import login from '@/components/index.vue'
import setting from '@/components/WaySetting.vue'
import personinfo from '@/components/EmployeeProfile.vue'
import carddata from '@/components/CardData.vue'
import cardapplication from '@/components/CardApplication.vue'
import fieldworkapplication from '@/components/FieldWorkApplication.vue'
import MainMenu from '@/components/MainMenu.vue'
import attendance from '@/components/Attendance.vue'
import ManagerInfo from '@/components/ManagerInfo.vue'
import ManagerMainMenu from '@/components/ManagerMainMenu.vue'
import leaveabsenceapproval from '@/components/LeaveAbsenceApproval.vue'
import fieldworkapproval from '@/components/FieldWorkApproval.vue'
import cardapproval from '@/components/CardApplicationApproval.vue'
import releasecheckin from '@/components/ReLeaseCheckIn.vue'
import leaveapplication from '@/components/LeaveApplication.vue'
import approvalnotice from '@/components/approvalNotice.vue'
const routes = [
  {
    path: '/',
    name: 'login',
    component: login,
  },
  {
    path: '/managermainmenu',
    name: 'managermainmenu',
    component: ManagerMainMenu,children:[
      {
        path: '/carddata',
        name: 'carddata',
        component: carddata,
      },
      {
        path: '/setting',
        name: 'setting',
        component: setting,
      },
      {
        path: '/managermainmenu/managerinfo',
        name: 'managerinfo',
        component: ManagerInfo,
      },
      {
        path: '/managermainmenu/leaveabsenceapproval',
        name: 'leaveabsenceapproval',
        component: leaveabsenceapproval,
      },
      {
        path: '/managermainmenu/fieldworkapproval',
        name: 'fieldworkapproval',
        component: fieldworkapproval,
      },
      {
        path: '/managermainmenu/cardapproval',
        name: 'cardapproval',
        component: cardapproval,
      },
      {
        path: '/managermainmenu/releasecheckin',
        name: 'releasecheckin',
        component: releasecheckin,
      },
    ]
  },
  {
    path: '/mainmenu',
    name: 'mainmune',
    component: MainMenu,children:[
      {
        path: '/mainmenu/personinfo',
        name: 'personinfo',
        component: personinfo,
      },
      {
        path: '/mainmenu/fieldworkapplication',
        name: 'fieldworkapplication',
        component: fieldworkapplication,
      },
      {
        path: '/mainmenu/attendance',
        name: 'attendance',
        component: attendance,
      },
      {
        path: '/mainmenu/cardapplication',
        name: 'cardapplication',
        component: cardapplication,
      },
      {
        path: '/mainmenu/leaveapplication',
        name: 'leaveapplication',
        component: leaveapplication,
      },
      {
        path: '/mainmenu/approvalnotice',
        name: 'approvalnotice',
        component: approvalnotice,
      },

    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router

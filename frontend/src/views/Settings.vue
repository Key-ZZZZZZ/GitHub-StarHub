<template>
  <div class="settings">
    <h2>系统设置</h2>
    
    <!-- 计划任务设置 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>计划任务设置</span>
        </div>
      </template>
      
      <el-form :model="schedulerForm" label-width="120px">
        <el-form-item label="每日任务时间">
          <el-time-picker
            v-model="schedulerForm.dailyTime"
            placeholder="选择时间"
            format="HH:mm"
          />
          <div class="form-tip">设置每日抓取GitHub热门项目的执行时间</div>
        </el-form-item>
        
        <el-form-item label="每周任务时间">
          <el-time-picker
            v-model="schedulerForm.weeklyTime"
            placeholder="选择时间"
            format="HH:mm"
          />
          <div class="form-tip">设置每周一抓取GitHub热门项目的执行时间</div>
        </el-form-item>
        
        <el-form-item label="自动可视化">
          <el-switch v-model="schedulerForm.autoVisualize" />
          <div class="form-tip">是否在抓取完成后自动生成可视化报告</div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSchedulerSettings">保存设置</el-button>
          <el-button @click="resetSchedulerSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 数据存储设置 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>数据存储设置</span>
        </div>
      </template>
      
      <el-form :model="storageForm" label-width="120px">
        <el-form-item label="数据保留策略">
          <el-select v-model="storageForm.retentionPolicy" placeholder="选择保留策略">
            <el-option label="保留所有数据" value="all" />
            <el-option label="仅保留最近30天" value="30days" />
            <el-option label="仅保留最近10次执行" value="10executions" />
          </el-select>
          <div class="form-tip">设置历史数据的保留策略</div>
        </el-form-item>
        
        <el-form-item label="数据存储路径">
          <el-input v-model="storageForm.dataPath" placeholder="数据存储路径" disabled />
          <div class="form-tip">GitHub热门项目数据的存储路径</div>
        </el-form-item>
        
        <el-form-item label="可视化存储路径">
          <el-input v-model="storageForm.visualizationPath" placeholder="可视化存储路径" disabled />
          <div class="form-tip">可视化报告的存储路径</div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveStorageSettings">保存设置</el-button>
          <el-button @click="resetStorageSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 系统信息 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>系统信息</span>
        </div>
      </template>
      
      <div class="system-info">
        <div class="info-item">
          <span class="info-label">系统版本:</span>
          <span class="info-value">1.0.0</span>
        </div>
        
        <div class="info-item">
          <span class="info-label">后端API地址:</span>
          <span class="info-value">http://localhost:5001</span>
        </div>
        
        <div class="info-item">
          <span class="info-label">数据目录:</span>
          <span class="info-value">{{ storageForm.dataPath }}</span>
        </div>
        
        <div class="info-item">
          <span class="info-label">可视化目录:</span>
          <span class="info-value">{{ storageForm.visualizationPath }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Settings',
  setup() {
    // 计划任务设置表单
    const schedulerForm = ref({
      dailyTime: new Date(2000, 0, 1, 8, 0), // 默认08:00
      weeklyTime: new Date(2000, 0, 1, 9, 0), // 默认09:00
      autoVisualize: true
    })
    
    // 数据存储设置表单
    const storageForm = ref({
      retentionPolicy: 'all',
      dataPath: 'data/',
      visualizationPath: 'data/visualizations/'
    })
    
    // 获取系统设置
    const fetchSettings = async () => {
      try {
        // 从后端API获取计划任务设置
        const response = await fetch('http://localhost:5001/api/scheduler/settings')
        if (!response.ok) {
          throw new Error(`获取设置失败: ${response.status}`)
        }
        
        const settings = await response.json()
        console.log('获取到的计划任务设置:', settings)
        
        // 设置时间选择器的值
        if (settings.daily_time) {
          const [hours, minutes] = settings.daily_time.split(':').map(Number)
          schedulerForm.value.dailyTime = new Date(2000, 0, 1, hours, minutes)
        }
        
        if (settings.weekly_time) {
          const [hours, minutes] = settings.weekly_time.split(':').map(Number)
          schedulerForm.value.weeklyTime = new Date(2000, 0, 1, hours, minutes)
        }
        
        // 获取数据目录信息
        storageForm.value.dataPath = 'data/'
        storageForm.value.visualizationPath = 'data/visualizations/'
      } catch (error) {
        console.error('获取系统设置失败:', error)
        ElMessage.error(`获取系统设置失败: ${error.message}`)
      }
    }
    
    // 保存计划任务设置
    const saveSchedulerSettings = async () => {
      try {
        // 格式化时间为字符串
        const dailyTime = `${schedulerForm.value.dailyTime.getHours().toString().padStart(2, '0')}:${schedulerForm.value.dailyTime.getMinutes().toString().padStart(2, '0')}`
        const weeklyTime = `${schedulerForm.value.weeklyTime.getHours().toString().padStart(2, '0')}:${schedulerForm.value.weeklyTime.getMinutes().toString().padStart(2, '0')}`
        
        // 调用后端API保存设置
        const response = await fetch('http://localhost:5001/api/scheduler/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            daily_time: dailyTime,
            weekly_time: weeklyTime
            // 注意：后端API目前不支持autoVisualize参数
          })
        })
        
        if (!response.ok) {
          throw new Error(`保存失败: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('保存计划任务设置结果:', result)
        
        ElMessage.success('计划任务设置已保存')
        
        // 重新获取最新设置以更新界面显示
        await fetchSettings()
      } catch (error) {
        console.error('保存计划任务设置失败:', error)
        ElMessage.error(`保存计划任务设置失败: ${error.message}`)
      }
    }
    
    // 重置计划任务设置
    const resetSchedulerSettings = () => {
      schedulerForm.value = {
        dailyTime: new Date(2000, 0, 1, 8, 0),
        weeklyTime: new Date(2000, 0, 1, 9, 0),
        autoVisualize: true
      }
    }
    
    // 保存数据存储设置
    const saveStorageSettings = async () => {
      try {
        // 这里应该调用后端API保存设置
        console.log('保存数据存储设置:', storageForm.value)
        
        ElMessage.success('数据存储设置已保存')
        
        // 重新获取最新设置以更新界面显示
        await fetchSettings()
      } catch (error) {
        console.error('保存数据存储设置失败:', error)
        ElMessage.error('保存数据存储设置失败')
      }
    }
    
    // 重置数据存储设置
    const resetStorageSettings = () => {
      storageForm.value = {
        retentionPolicy: 'all',
        dataPath: 'data/',
        visualizationPath: 'data/visualizations/'
      }
    }
    
    onMounted(() => {
      fetchSettings()
    })
    
    return {
      schedulerForm,
      storageForm,
      saveSchedulerSettings,
      resetSchedulerSettings,
      saveStorageSettings,
      resetStorageSettings
    }
  }
}
</script>

<style scoped>
.settings {
  padding: 0 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
}

.info-label {
  width: 120px;
  color: #606266;
}

.info-value {
  font-weight: bold;
}
</style>
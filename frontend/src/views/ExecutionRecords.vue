<template>
  <div class="execution-records">
    <h2>执行记录</h2>
    
    <!-- 任务操作区域 -->
    <el-card class="operation-card">
      <template #header>
        <div class="card-header">
          <span>任务操作</span>
        </div>
      </template>
      
      <div class="operation-section">
        <div class="manual-operation">
          <h3>手动执行</h3>
          <div class="button-group">
            <el-button type="primary" @click="runDailyTask">
              <el-icon><VideoPlay /></el-icon> 执行日榜抓取
            </el-button>
            <el-button type="primary" @click="runWeeklyTask">
              <el-icon><VideoPlay /></el-icon> 执行周榜抓取
            </el-button>
          </div>
        </div>
        
        <div class="scheduled-operation">
          <h3>计划任务</h3>
          <div class="scheduler-controls">
            <el-radio-group v-model="schedulerStatus" @change="handleSchedulerStatusChange">
              <el-radio :label="'running'">开启计划任务</el-radio>
              <el-radio :label="'stopped'">暂停计划任务</el-radio>
            </el-radio-group>
          </div>
        </div>
      </div>
      
      <!-- 调度器状态 -->
      <div class="scheduler-status" v-if="schedulerInfo.daily_task">
        <h3>调度器状态</h3>
        <div class="status-items">
          <div class="status-item">
            <span class="label">每日抓取任务:</span>
            <el-tag :type="schedulerInfo.daily_task.status === 'running' ? 'success' : 'info'">
              {{ schedulerInfo.daily_task.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
            <span class="next-run" v-if="schedulerInfo.daily_task.next_run">
              下次执行时间: {{ schedulerInfo.daily_task.next_run }}
            </span>
          </div>
          
          <div class="status-item">
            <span class="label">每周抓取任务:</span>
            <el-tag :type="schedulerInfo.weekly_task.status === 'running' ? 'success' : 'info'">
              {{ schedulerInfo.weekly_task.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
            <span class="next-run" v-if="schedulerInfo.weekly_task.next_run">
              下次执行时间: {{ schedulerInfo.weekly_task.next_run }}
            </span>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 统计数据卡片 -->
    <div class="statistics-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">总执行次数</div>
              <div class="stat-value">{{ statistics.totalExecutions }}</div>
              <div class="stat-desc">最近一次: {{ statistics.lastExecutionTime }}</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">每日榜抓取次数</div>
              <div class="stat-value">{{ statistics.dailyExecutions }}</div>
              <div class="stat-desc">最近一次: {{ statistics.lastDailyTime }}</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">每周榜抓取次数</div>
              <div class="stat-value">{{ statistics.weeklyExecutions }}</div>
              <div class="stat-desc">最近一次: {{ statistics.lastWeeklyTime }}</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">平均执行耗时</div>
              <div class="stat-value">{{ statistics.avgExecutionTime }}</div>
              <div class="stat-desc">总计抓取项目数: {{ statistics.totalProjects }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 最近执行记录表格 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>最近执行记录</span>
          <el-button class="view-all-btn" text @click="viewAllHistory">查看全部</el-button>
        </div>
      </template>
      
      <el-table :data="executionHistory" style="width: 100%">
        <el-table-column prop="executionTime" label="执行时间" width="180" header-align="center" align="center">
          <template #default="scope">
            {{ formatTimestamp(scope.row.executionTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" header-align="center" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'daily' ? 'primary' : 'success'">
              {{ scope.row.type === 'daily' ? '每日榜' : '每周榜' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" header-align="center" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="finishTime" label="完成时间" width="180" header-align="center" align="center">
          <template #default="scope">
            {{ formatTimestamp(scope.row.finishTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="count" label="总数" width="80" header-align="center" align="center" />
        <el-table-column prop="stars" label="星标" width="80" header-align="center" align="center" />
        <el-table-column prop="updates" label="更新" width="80" header-align="center" align="center" />
        <el-table-column prop="duration" label="耗时" width="80" header-align="center" align="center" />
        <el-table-column label="操作" width="120" header-align="center" align="center">
          <template #default="scope">
            <el-button text type="primary" @click="viewDetail(scope.row)">查看详情</el-button>
            <el-button text type="danger" @click="deleteRecord(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 执行记录详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="执行记录详情"
      width="80%"
      destroy-on-close
      
    >
      <div v-if="recordDetail" class="record-detail">
        <!-- 基本信息区域 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="label">执行ID:</span>
              <span class="value">#{{ recordDetail.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">执行类型:</span>
              <span class="value">{{ recordDetail.type === 'daily' ? '每日榜' : '每周榜' }}</span>
            </div>
            <div class="info-item">
              <span class="label">开始时间:</span>
              <span class="value">{{ recordDetail.executionTime }}</span>
            </div>
            <div class="info-item">
              <span class="label">结束时间:</span>
              <span class="value">{{ recordDetail.finishTime }}</span>
            </div>
            <div class="info-item">
              <span class="label">执行状态:</span>
              <el-tag :type="getStatusType(recordDetail.status)">{{ getStatusText(recordDetail.status) }}</el-tag>
            </div>
            <div class="info-item">
              <span class="label">执行耗时:</span>
              <span class="value">{{ recordDetail.duration }}</span>
            </div>
          </div>
        </el-card>
        
        <!-- 统计信息区域 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>抓取结果统计</span>
            </div>
          </template>
          
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ recordDetail.count }}</div>
              <div class="stat-label">抓取项目总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ recordDetail.stars }}</div>
              <div class="stat-label">星标总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ recordDetail.updates }}</div>
              <div class="stat-label">更新项目数</div>
            </div>
          </div>
        </el-card>
        
        <!-- 原始内容区域 -->
        <!-- <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>原始内容</span>
            </div>
          </template>
          <el-input
            v-model="recordDetail.content"
            type="textarea"
            :rows="10"
            readonly
            placeholder="无原始内容"
          ></el-input>
        </el-card> -->

        <!-- 项目列表区域 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>抓取项目列表</span>
              <div class="filter-actions">
                <el-input
                  v-model="projectSearchKeyword"
                  placeholder="搜索项目"
                  prefix-icon="Search"
                  clearable
                  @input="filterRecordProjects"
                  style="width: 200px;"
                />
                <el-select v-model="projectLanguageFilter" placeholder="编程语言" clearable @change="filterRecordProjects">
                  <el-option
                    v-for="item in projectLanguages"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
                <el-select v-model="projectSortBy" placeholder="排序方式" @change="sortRecordProjects">
                  <el-option label="星标数量 (高到低)" value="stars-desc" />
                  <el-option label="星标数量 (低到高)" value="stars-asc" />
                  <el-option label="最近更新" value="updated" />
                </el-select>
              </div>
            </div>
          </template>
          
          <el-table
            :data="displayRecordProjects"
            style="width: 100%"
            :default-sort="{prop: 'stars', order: 'descending'}"
          >
            <el-table-column label="项目名称" min-width="200">
              <template #default="scope">
                <div class="project-name">
                  <div class="project-info">
                    <a :href="scope.row.url" target="_blank" class="project-link">{{ scope.row.name }}</a>
                    <div class="project-desc">{{ scope.row.description }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="language" label="语言" width="120">
              <template #default="scope">
                <el-tag>{{ scope.row.language }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="stars" label="星标数" width="120" sortable />
            
            <el-table-column prop="forks" label="分支数" width="120" sortable />
            
            <el-table-column prop="todayStars" label="今日星标" width="120">
              <template #default="scope">
                <span class="today-stars">+{{ scope.row.todayStars }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" header-align="center" align="center">
              <template #default="scope">
                <el-button text type="primary" @click="viewProjectDetails(scope.row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="recordProjectsPage"
              v-model:page-size="recordProjectsPageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredRecordProjects.length"
              @size-change="handleRecordProjectsSizeChange"
              @current-change="handleRecordProjectsPageChange"
            />
          </div>
        </el-card>
      </div>
    </el-dialog>

    <!-- 查看全部执行记录对话框 -->
    <el-dialog
      v-model="allHistoryDialogVisible"
      title="全部执行记录"
      width="90%"
      destroy-on-close
    >
      <el-table :data="paginatedAllExecutionHistory" style="width: 100%">
        <el-table-column prop="executionTime" label="执行时间" width="180" header-align="center" align="center">
          <template #default="scope">
            {{ formatTimestamp(scope.row.executionTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" header-align="center" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'daily' ? 'primary' : 'success'">
              {{ scope.row.type === 'daily' ? '每日榜' : '每周榜' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" header-align="center" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="finishTime" label="完成时间" width="180" header-align="center" align="center">
          <template #default="scope">
            {{ formatTimestamp(scope.row.finishTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="count" label="总数" width="80" header-align="center" align="center" />
        <el-table-column prop="stars" label="星标" width="80" header-align="center" align="center" />
        <el-table-column prop="updates" label="更新" width="80" header-align="center" align="center" />
        <el-table-column prop="duration" label="耗时" width="80" header-align="center" align="center" />
        <el-table-column label="操作" width="120" header-align="center" align="center">
          <template #default="scope">
            <el-button text type="primary" @click="viewDetail(scope.row)">查看详情</el-button>
            <el-button text type="danger" @click="deleteRecord(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="allHistoryCurrentPage"
          v-model:page-size="allHistoryPageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="allHistoryTotal"
          @size-change="handleAllHistorySizeChange"
          @current-change="handleAllHistoryPageChange"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { VideoPlay } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'ExecutionRecords',
  components: {
    VideoPlay
  },
  setup() {
    const executionHistory = ref([])
    const schedulerStatus = ref('stopped')
    const schedulerInfo = ref({
      daily_task: { status: 'idle', next_run: '' },
      weekly_task: { status: 'idle', next_run: '' }
    })
    const statistics = ref({
      totalExecutions: 0,
      lastExecutionTime: '',
      dailyExecutions: 0,
      lastDailyTime: '',
      weeklyExecutions: 0,
      lastWeeklyTime: '',
      avgExecutionTime: '0',
      totalProjects: '0'
    })
    
    // 详情对话框相关
    const detailDialogVisible = ref(false)
    const recordDetail = ref(null)
    const recordProjects = ref([])
    const projectSearchKeyword = ref('')
    const projectLanguageFilter = ref('')
    const projectSortBy = ref('stars-desc')
    const recordProjectsPage = ref(1)
    const recordProjectsPageSize = ref(10)
    const projectLanguages = ref([])

    // 查看全部历史记录相关
    const allRawExecutionHistory = ref([]) // 存储所有原始执行历史记录
    const allHistoryDialogVisible = ref(false)
    const allHistoryCurrentPage = ref(1)
    const allHistoryPageSize = ref(10)
    const allHistoryTotal = computed(() => allRawExecutionHistory.value.length)

    const paginatedAllExecutionHistory = computed(() => {
      const start = (allHistoryCurrentPage.value - 1) * allHistoryPageSize.value
      const end = start + allHistoryPageSize.value
      return allRawExecutionHistory.value.slice(start, end)
    })
    
    // 格式化时间戳为可读日期时间
    const formatTimestamp = (timestamp) => {
      // 检查时间戳格式，处理不同可能的格式
      if (!timestamp) return '-';
      
      // 后端已经返回格式化的时间字符串，直接使用
      if (typeof timestamp === 'string' && timestamp.includes('-') && timestamp.includes(':')) {
        return timestamp;
      }
      
      // 尝试解析时间戳格式
      let date;
      if (typeof timestamp === 'string' && timestamp.length === 14) { // 格式如: 20250512_121431
        const year = timestamp.substring(0, 4);
        const month = timestamp.substring(4, 6);
        const day = timestamp.substring(6, 8);
        const hour = timestamp.substring(9, 11);
        const minute = timestamp.substring(11, 13);
        const second = timestamp.substring(13, 15);
        date = new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);
      } else {
        // 尝试直接解析
        date = new Date(timestamp);
      }
      
      // 检查日期是否有效
      if (isNaN(date.getTime())) return timestamp; // 如果无效则返回原始值
      
      // 格式化为易读格式: YYYY-MM-DD HH:MM:SS
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    };
    
    // 获取执行历史记录
    const fetchExecutionHistory = async () => {
      try {
        const response = await axios.get('http://localhost:5001/api/execution-history')
        
        if (!response.data || !Array.isArray(response.data)) {
          console.error('后端返回的数据格式不正确:', response.data)
          ElMessage.warning('获取执行记录数据格式不正确')
          return
        }
        
        // 处理响应数据，转换为表格所需格式
        executionHistory.value = response.data.map(item => {
          return {
            id: item.id,
            executionTime: item.execution_time || '-',
            type: item.type || '',
            finishTime: item.finishTime || '-',
            count: item.count || 0,
            stars: item.stars || 0,
            updates: item.updates || 0,
            duration: item.duration || '-',
            status: item.status || 'unknown'
          };
        })
        
        // 存储所有原始记录
        allRawExecutionHistory.value = response.data.map(item => {
          return {
            id: item.id,
            executionTime: item.execution_time || '-',
            type: item.type || '',
            finishTime: item.finishTime || '-',
            count: item.count || 0,
            stars: item.stars || 0,
            updates: item.updates || 0,
            duration: item.duration || '-',
            status: item.status || 'unknown'
          };
        })

        // 只显示最近6条记录用于主页面的“最近执行记录”部分
        executionHistory.value = allRawExecutionHistory.value.slice(0, 6)
        
        // 更新统计数据
        if (response.data.length > 0) {
          // 计算总执行次数
          statistics.value.totalExecutions = response.data.length
          
          // 获取最新的执行时间（第一条记录）
          const latestRecord = response.data[0]
          statistics.value.lastExecutionTime = latestRecord.execution_time || '-'
          
          // 分别计算每日榜和每周榜的执行次数和最新执行时间
          const dailyRecords = response.data.filter(item => item.type === 'daily')
          const weeklyRecords = response.data.filter(item => item.type === 'weekly')
          
          statistics.value.dailyExecutions = dailyRecords.length
          if (dailyRecords.length > 0) {
            statistics.value.lastDailyTime = dailyRecords[0].execution_time || '-'
          } else {
            statistics.value.lastDailyTime = '-'
          }
          
          statistics.value.weeklyExecutions = weeklyRecords.length
          if (weeklyRecords.length > 0) {
            statistics.value.lastWeeklyTime = weeklyRecords[0].execution_time || '-'
          } else {
            statistics.value.lastWeeklyTime = '-'
          }
          
          // 计算平均执行时间 - 使用数据库中的duration字段
          const completedRecords = response.data.filter(item => 
            item.status === 'completed' && item.duration && !isNaN(parseFloat(item.duration)))
          
          if (completedRecords.length > 0) {
            const totalDuration = completedRecords.reduce((sum, record) => {
              // 从字符串中提取数值部分（去掉's'后缀）
              const durationStr = String(record.duration || '0')
              const duration = parseFloat(durationStr.replace('s', '')) || 0
              return sum + duration
            }, 0)
            statistics.value.avgExecutionTime = (totalDuration / completedRecords.length).toFixed(1) + 's'
          } else {
            statistics.value.avgExecutionTime = '0.0s'
          }
          
          // 计算总项目数
          const totalProjects = response.data.reduce((sum, record) => sum + (record.count || 0), 0)
          statistics.value.totalProjects = totalProjects.toString()
        } else {
          // 如果没有记录，重置统计数据
          statistics.value = {
            totalExecutions: 0,
            lastExecutionTime: '-',
            dailyExecutions: 0,
            lastDailyTime: '-',
            weeklyExecutions: 0,
            lastWeeklyTime: '-',
            avgExecutionTime: '0.0s',
            totalProjects: '0'
          }
        }
      } catch (error) {
        console.error('获取执行历史记录失败:', error)
        ElMessage.error('获取执行历史记录失败: ' + (error.message || '未知错误'))
      }
    }
    
    // 获取调度器状态
    const fetchSchedulerStatus = async () => {
      try {
        const response = await axios.get('http://localhost:5001/api/scheduler-status')
        schedulerInfo.value = response.data
        schedulerStatus.value = response.data.daily_task.status === 'running' ? 'running' : 'stopped'
      } catch (error) {
        console.error('获取调度器状态失败:', error)
      }
    }
    


    // 处理“查看全部”历史记录的分页变化
    const handleAllHistoryPageChange = (newPage) => {
      allHistoryCurrentPage.value = newPage
    }

    // 处理“查看全部”历史记录的每页大小变化
    const handleAllHistorySizeChange = (newSize) => {
      allHistoryPageSize.value = newSize
      allHistoryCurrentPage.value = 1 // 改变每页大小时重置到第一页
    }

    // 运行每日任务
    const runDailyTask = async () => {
      try {
        ElMessage.info('正在执行每日榜抓取任务...')
        const response = await axios.post('http://localhost:5001/api/run-daily')
        ElMessage.success(response.data.message || '每日榜抓取任务执行成功')
        // 刷新数据
        fetchExecutionHistory()
        fetchSchedulerStatus()
      } catch (error) {
        console.error('执行每日榜抓取任务失败:', error)
        ElMessage.error('执行每日榜抓取任务失败: ' + ((error.response && error.response.data && error.response.data.message) || error.message))
      }
    }
    
    // 运行每周任务
    const runWeeklyTask = async () => {
      try {
        ElMessage.info('正在执行每周榜抓取任务...')
        const response = await axios.post('http://localhost:5001/api/run-weekly')
        ElMessage.success(response.data.message || '每周榜抓取任务执行成功')
        // 刷新数据
        fetchExecutionHistory()
        fetchSchedulerStatus()
      } catch (error) {
        console.error('执行每周榜抓取任务失败:', error)
        ElMessage.error('执行每周榜抓取任务失败: ' + ((error.response && error.response.data && error.response.data.message) || error.message))
      }
    }
    
    // 处理调度器状态变更
    // 查看全部历史记录
    const viewAllHistory = () => {
      allHistoryDialogVisible.value = true
      allHistoryCurrentPage.value = 1 // 打开对话框时重置到第一页
    }

    const handleSchedulerStatusChange = async (status) => {
      try {
        if (status === 'running') {
          ElMessage.info('正在启动计划任务...')
          await axios.post('http://localhost:5001/api/start-scheduler')
          ElMessage.success('计划任务已启动')
        } else {
          ElMessage.info('正在停止计划任务...')
          await axios.post('http://localhost:5001/api/stop-scheduler')
          ElMessage.success('计划任务已停止')
        }
        // 操作完成后强制刷新调度器状态，并始终依赖 fetchSchedulerStatus 的结果
        await fetchSchedulerStatus()
      } catch (error) {
        console.error('更改调度器状态失败:', error)
        ElMessage.error('更改调度器状态失败: ' + ((error.response && error.response.data && error.response.data.message) || error.message))
        // 恢复之前的状态
        await fetchSchedulerStatus()
      }
    }
    

    
    // 获取状态类型对应的标签类型
    const getStatusType = (status) => {
      switch (status) {
        case 'completed':
          return 'success'
        case 'running':
          return 'warning'
        case 'failed':
          return 'danger'
        default:
          return 'info'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'completed':
          return '已完成'
        case 'running':
          return '执行中'
        case 'failed':
          return '失败'
        default:
          return '未知'
      }
    }
    
    // 查看详情
    // 查看详情
    const viewDetail = async (record) => {
    try {
    detailDialogVisible.value = true
    
    // 获取执行记录详情数据
    const response = await axios.get(`http://localhost:5001/api/execution-detail/${record.id}`)
    if (response.data && response.data.record) {
    // 正确映射后端返回的数据结构
    recordDetail.value = {
        id: response.data.record.id,
        type: response.data.record.type,
        executionTime: response.data.record.start_time,
        finishTime: response.data.record.end_time,
        status: response.data.record.status,
        count: response.data.record.project_count,
        stars: response.data.record.stars_count,  // 正确映射星标总数
        updates: response.data.record.updates_count,
        duration: response.data.record.duration,
        content: response.data.record.content || '' // 添加 content 字段，确保其存在
    }
    
    // 处理项目列表
    if (response.data.projects) {
       recordProjects.value = response.data.projects
    
    // 提取所有语言选项
    const languages = new Set()
    recordProjects.value.forEach(project => {
        if (project.language) {
          languages.add(project.language)
        }
    })
     projectLanguages.value = Array.from(languages).sort()

    // 初始化筛选结果
    filteredProjects.value = [...recordProjects.value]

    // 初始化筛选和排序
    filterRecordProjects()
    } else {
        recordProjects.value = []
        filteredProjects.value = []
        projectLanguages.value = []
    }
    } else {
        recordProjects.value = []
        filteredProjects.value = []
        projectLanguages.value = []
        ElMessage.warning('未找到相关项目数据')
    }
    } catch (error) {
        console.error('获取执行记录详情失败:', error)
        ElMessage.error('获取执行记录详情失败: ' + (error.message || '未知错误'))
    }
    }
    
    // 筛选项目
    const filterRecordProjects = () => {
      // 实现筛选逻辑
      filteredProjects.value = recordProjects.value.filter(project => {
        // 关键词筛选 - 匹配项目名称和描述
        const keywordMatch = !projectSearchKeyword.value || 
          (project.name && project.name.toLowerCase().includes(projectSearchKeyword.value.toLowerCase())) ||
          (project.description && project.description.toLowerCase().includes(projectSearchKeyword.value.toLowerCase()));
        
        // 语言筛选
        const languageMatch = !projectLanguageFilter.value || 
          project.language === projectLanguageFilter.value;
        
        return keywordMatch && languageMatch;
      });
      
      // 应用排序
      sortRecordProjects();
      
      // 重置到第一页
      recordProjectsPage.value = 1;
    }
    
    // 排序项目
    const sortRecordProjects = () => {
      // 实现排序逻辑
      if (!filteredProjects.value) return;
      
      switch (projectSortBy.value) {
        case 'stars-desc':
          filteredProjects.value.sort((a, b) => b.stars - a.stars);
          break;
        case 'stars-asc':
          filteredProjects.value.sort((a, b) => a.stars - b.stars);
          break;
        case 'updated':
          filteredProjects.value.sort((a, b) => {
            if (!a.updatedAt) return 1;
            if (!b.updatedAt) return -1;
            return new Date(b.updatedAt) - new Date(a.updatedAt);
          });
          break;
        default:
          // 默认按星标数降序
          filteredProjects.value.sort((a, b) => b.stars - a.stars);
      }
    }
    
    // 添加一个新的 ref 来存储筛选后的结果
    const filteredProjects = ref([]);
    
    // 更新计算属性：筛选后的项目
    const filteredRecordProjects = computed(() => {
      return filteredProjects.value;
    })
    
    // 处理页码变化
    const handleRecordProjectsPageChange = (page) => {
      recordProjectsPage.value = page
    }
    
    // 处理每页显示数量变化
    const handleRecordProjectsSizeChange = (size) => {
      recordProjectsPageSize.value = size
      recordProjectsPage.value = 1 // 重置到第一页
    }
    
    // 计算属性：筛选后的项目
    const displayRecordProjects = computed(() => {
      const start = (recordProjectsPage.value - 1) * recordProjectsPageSize.value
      const end = start + recordProjectsPageSize.value
      return filteredRecordProjects.value.slice(start, end)
    })
    
    // 查看项目详情
    const viewProjectDetails = (project) => {
      // 实现查看项目详情的逻辑
      console.log('查看项目详情:', project.name);
      // 可以跳转到项目详情页或打开新窗口访问GitHub
      window.open(` https://github.com/${project.name} `, '_blank');
    }

    // 删除执行记录
    const deleteRecord = async (record) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除ID为 ${record.id} 的执行记录吗？此操作将同时删除所有关联的抓取项目，且无法恢复。`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        );

        ElMessage.info('正在删除执行记录...')
        await axios.delete(`http://localhost:5001/api/execution-record/${record.id}`)
        ElMessage.success('执行记录删除成功')
        // 刷新数据
        fetchExecutionHistory()
        // 如果详情对话框打开且是当前记录，则关闭
        if (detailDialogVisible.value && recordDetail.value && recordDetail.value.id === record.id) {
          detailDialogVisible.value = false;
        }
      } catch (error) {
        if (error === 'cancel') {
          ElMessage.info('已取消删除操作');
        } else {
          console.error('删除执行记录失败:', error)
          ElMessage.error('删除执行记录失败: ' + ((error.response && error.response.data && error.response.data.message) || error.message))
        }
      }
    }

    onMounted(() => {
      fetchExecutionHistory()
      fetchSchedulerStatus()
    })
    
    return {
      executionHistory,
      schedulerStatus,
      schedulerInfo,
      statistics,
      detailDialogVisible,
      recordDetail,
      projectSearchKeyword,
      projectLanguageFilter,
      projectSortBy,
      recordProjectsPage,
      recordProjectsPageSize,
      projectLanguages,
      allHistoryDialogVisible,
      allHistoryCurrentPage,
      allHistoryPageSize,
      allHistoryTotal,
      paginatedAllExecutionHistory,
      formatTimestamp,
      fetchExecutionHistory,
      fetchSchedulerStatus,
      runDailyTask,
      runWeeklyTask,
      handleSchedulerStatusChange,
      getStatusType,
      getStatusText,
      viewDetail,
      filteredRecordProjects,
      displayRecordProjects,
      filterRecordProjects,
      sortRecordProjects,
      handleRecordProjectsSizeChange,
      handleRecordProjectsPageChange,
      viewProjectDetails,
      viewAllHistory,
      handleAllHistoryPageChange,
      handleAllHistorySizeChange,
      deleteRecord
    }
  }
}
</script>

<style >
.execution-records {
  padding: 20px;
}

.operation-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.operation-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.manual-operation,
.scheduled-operation {
  flex: 1;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.scheduler-controls {
  margin-top: 10px;
}

.scheduler-status {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.status-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.next-run {
  margin-left: 10px;
  color: #909399;
  font-size: 0.9em;
}

.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.stat-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
}

.history-card {
  margin-bottom: 20px;
}

.record-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  margin-bottom: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
}

.label {
  font-weight: bold;
  margin-right: 10px;
  color: #606266;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  text-align: center;
}

.stat-item {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #606266;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.project-name {
  display: flex;
  align-items: center;
}

.project-info {
  display: flex;
  flex-direction: column;
}

.project-link {
  color: #409eff;
  text-decoration: none;
  font-weight: bold;
}

.project-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.today-stars {
  color: #67c23a;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.view-all-btn {
  padding: 0;
}
.el-dialog{
  margin-top: 8vh !important;
}

</style>
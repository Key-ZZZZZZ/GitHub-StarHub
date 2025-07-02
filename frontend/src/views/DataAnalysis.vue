<template>
  <div class="data-analysis">
    <h2>数据分析</h2>
    
    <!-- 分析类型选择 -->
    <el-card class="filter-card">
      <div class="filter-section">
        <el-radio-group v-model="analysisType" @change="handleTypeChange">
          <el-radio-button label="daily">每日榜分析</el-radio-button>
          <el-radio-button label="weekly">每周榜分析</el-radio-button>
        </el-radio-group>
        
        <el-select
          v-model="selectedDate"
          placeholder="选择日期"
          @change="handleDateChange"
          style="width: 200px;"
        >
          <el-option
            v-for="item in dateOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </div>
    </el-card>
    
    <!-- 图表展示区域 -->
    <div class="charts-container">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>编程语言分布</span>
              </div>
            </template>
            <div class="chart" ref="languageChartRef"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>星标数量分布</span>
              </div>
            </template>
            <div class="chart" ref="starsChartRef"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目创建时间分布</span>
              </div>
            </template>
            <div class="chart" ref="timeChartRef"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
  <ProjectDetailDialog :showDialog="showProjectDetailDialog" :projects="selectedProject" @close="closeProjectDetailDialog"/>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import ProjectDetailDialog from '../components/ProjectDetailDialog.vue'

export default {
  name: 'DataAnalysis',
  components: { ProjectDetailDialog }, // 注册组件
  setup() {
    const analysisType = ref('daily')
    const selectedDate = ref('')
    const dateOptions = ref([])
    
    // 项目详情对话框相关
    const showProjectDetailDialog = ref(false)
    const selectedProject = ref(null)
    
    // 图表引用
    const languageChartRef = ref(null)
    const starsChartRef = ref(null)
    const timeChartRef = ref(null)
    
    // 图表实例
    let languageChart = null
    let starsChart = null
    let timeChart = null
    
    // 初始化日期选项
    const initDateOptions = async () => {
      try {
        const response = await axios.get(`http://localhost:5001/api/trending/dates?type=${analysisType.value}`)
        console.log('获取日期选项响应 (原始数据):', response.data); // 打印后端返回的原始日期字符串数组
        dateOptions.value = response.data.map(dateStr => {
          // 尝试将日期字符串解析为 UTC 时间，避免本地时区影响
          const date = new Date(dateStr + 'T00:00:00Z');
          console.log(`处理日期: dateStr = "${dateStr}", new Date(dateStr + 'T00:00:00Z') = ${date}`);
          // 格式化 label，确保显示完整的年份
          const formattedLabel = date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'UTC' }); // 明确指定时区为 UTC
          console.log(`格式化标签: ${formattedLabel}`);
          return {
            label: formattedLabel,
            value: dateStr // 保持 value 为原始的 YYYY-MM-DD 字符串，以便后续请求使用
          }
        })
        
        if (dateOptions.value.length > 0) {
          selectedDate.value = dateOptions.value[0].value
          fetchAnalysisData()
        } else {
          selectedDate.value = ''
          // 清空图表
          updateCharts({}, {}, {})
        }
      } catch (error) {
        console.error('获取日期选项失败:', error)
        ElMessage.error('获取日期选项失败')
      }
    }
    
    // 初始化图表
    const initCharts = () => {
      languageChart = echarts.init(languageChartRef.value)
      starsChart = echarts.init(starsChartRef.value)
      timeChart = echarts.init(timeChartRef.value)
      
      // 初始设置空数据
      updateCharts({}, {}, {})
    }
    
    // 打开项目详情对话框
    const openProjectDetailDialog = (projects) => {
      selectedProject.value = projects
      showProjectDetailDialog.value = true
    }
    
    // 关闭项目详情对话框
    const closeProjectDetailDialog = () => {
      showProjectDetailDialog.value = false
      selectedProject.value = null
    }
    
    // 处理分析类型变化
    const handleTypeChange = () => {
      initDateOptions()
    }
    
    // 处理日期变化
    const handleDateChange = () => {
      fetchAnalysisData()
    }
    
    // 获取分析数据
    const fetchAnalysisData = async () => {
      if (!selectedDate.value) {
        // 清空图表
        updateCharts({}, {}, {})
        return
      }
      try {
        const response = await axios.get(`http://localhost:5001/api/analysis-data?type=${analysisType.value}&date=${selectedDate.value}`)
        console.log('获取分析数据响应:', response.data);
        const { language_distribution, stars_distribution, time_distribution } = response.data
        console.log('Time Data:', time_distribution); // 添加这行来打印 time_distribution
        console.log('Fetched analysis data:', response.data);
        console.log('languageData:', language_distribution);
        console.log('starsData:', stars_distribution);
        console.log('timeData:', time_distribution);
        updateCharts(language_distribution, stars_distribution, time_distribution)
      } catch (error) {
        console.error('获取分析数据失败:', error)
        ElMessage.error('获取分析数据失败: ' + (error.response && error.response.data && error.response.data.error || error.message));
        // 清空图表
        updateCharts({}, {}, {})
      }
    }
    
    // 更新图表数据
    const updateCharts = (languageData, starsData, timeData) => {
      // 语言分布图表
      if (languageChart) {
        languageChart.setOption({
          title: {
            text: '编程语言分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'horizontal',
            top: 'auto',
            bottom: 0,
            type: 'scroll',
            height: 120, // 设置图例高度，使其可以滚动
            data: Array.isArray(languageData) ? languageData.map(item => item.name) : [],
            itemGap: 5,
            textStyle: {
              fontSize: 12
            }
          },
          series: [
            {
              name: '编程语言分布',
              type: 'pie',
              radius: ['40%', '70%'],
              center: ['50%', '50%'],
              avoidLabelOverlap: false,
              itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
              },
              label: {
                show: false,
                position: 'center'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: '20',
                  fontWeight: 'bold'
                }
              },
              labelLine: {
                show: false
              },
              data: Array.isArray(languageData) ? languageData.map(item => ({ value: item.value, name: item.name })) : []
            }
          ]
        })
        
        // 添加点击事件监听器
        languageChart.off('click'); // 移除旧的监听器，防止重复添加
        languageChart.on('click', (params) => {
          if (params.data && params.name) {
            fetchProjectsAndShowDialog('language', params.name);
          }
        });
      }

      // 星标数量图表
      if (starsChart) {
        starsChart.setOption({
          title: {
            text: '星标数量分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'horizontal',
            top: 'auto',
            bottom: 0,
            type: 'scroll',
            height: 120, // 设置图例高度，使其可以滚动
            data: Array.isArray(starsData) ? starsData.map(item => item.name) : [],
            itemGap: 5,
            textStyle: {
              fontSize: 12
            }
          },
          series: [
            {
              name: '星标数量分布',
              type: 'pie',
              radius: ['40%', '70%'],
              center: ['50%', '50%'],
              avoidLabelOverlap: false,
              itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
              },
              label: {
                show: false,
                position: 'center'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: '20',
                  fontWeight: 'bold'
                }
              },
              labelLine: {
                show: false
              },
              data: Array.isArray(starsData) ? starsData.map(item => ({ value: item.value, name: item.name })) : []
            }
          ]
        })

        // 添加点击事件监听器
        starsChart.off('click'); // 移除旧的监听器，防止重复添加
        starsChart.on('click', (params) => {
          if (params.data && params.name) {
            fetchProjectsAndShowDialog('stars', params.name);
          }
        });
      }

      // 项目创建时间分布图表
      if (timeChart) {
        // 根据 analysisType 调整 xAxis 的格式
        let xAxisData = [];
        let xAxisFormatter = '';

        if (Array.isArray(timeData)) {
          xAxisData = timeData.map(item => item.name);
          if (analysisType.value === 'daily') {
            // 每日榜显示具体日期
            xAxisFormatter = function (value) {
              return value; // 后端已经格式化为 YYYY-MM-DD
            };
          } else if (analysisType.value === 'weekly') {
            // 每周榜显示周数或月份
            xAxisFormatter = function (value) {
              // value 格式为 YYYY-WW，可以进一步格式化为更友好的显示
              const year = value.substring(0, 4);
              const week = value.substring(5);
              return `${year}年第${week}周`;
            };
          }
        }

        timeChart.setOption({
          title: {
            text: '项目创建时间分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: xAxisData,
            axisLabel: {
              interval: 0,
              rotate: 30,
              formatter: xAxisFormatter
            }
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '项目数量',
              type: 'bar',
              data: Array.isArray(timeData) ? timeData.map(item => item.value) : [],
              itemStyle: {
                color: new echarts.graphic.LinearGradient(
                  0, 0, 0, 1,
                  [
                    { offset: 0, color: '#83bff6' },
                    { offset: 0.5, color: '#188df0' },
                    { offset: 1, color: '#188df0' }
                  ]
                )
              },
              emphasis: {
                itemStyle: {
                  color: new echarts.graphic.LinearGradient(
                    0, 0, 0, 1,
                    [
                      { offset: 0, color: '#2378f7' },
                    { offset: 0.7, color: '#2378f7' },
                    { offset: 1, color: '#83bff6' }
                  ]
                  )
                }
              }
            }
          ]
        })

        // 添加点击事件监听器
        timeChart.off('click'); // 移除旧的监听器，防止重复添加
        timeChart.on('click', (params) => {
          if (params.data && params.name) {
            fetchProjectsAndShowDialog('time', params.name);
          }
        });
      }
    }

    // 根据点击的图表数据获取项目详情并显示对话框
    function fetchProjectsAndShowDialog(chartType, value) {
      console.log(`fetchProjectsAndShowDialog called with chartType: ${chartType}, value: ${value}`);
      let params = {
        type: analysisType.value,
        date: selectedDate.value,
      }

      if (chartType === 'language') {
        params.language = value
      } else if (chartType === 'stars') {
        const [min, max] = value.split('-').map(s => s.replace('+', ''))
        params.stars_min = parseInt(min)
        if (max) {
          params.stars_max = parseInt(max)
        } else {
          params.stars_max = null // 表示没有上限
        }
      } else if (chartType === 'time') {
        if (analysisType.value === 'daily') {
          // 对于每日榜，value 是 YYYY-MM-DD 格式的日期
          params.captured_at_start = `${value} 00:00:00`
          params.captured_at_end = `${value} 23:59:59`
        } else if (analysisType.value === 'weekly') {
          // 对于每周榜，value 是 YYYY-WW 格式的周数
          // 需要将周数转换为日期范围
          const [year, week] = value.split('-').map(Number)
          const firstDayOfWeek = new Date(year, 0, 1 + (week - 1) * 7)
          // 找到当年的第一个周一
          const day = firstDayOfWeek.getDay()
          const diff = firstDayOfWeek.getDate() - day + (day === 0 ? -6 : 1) // adjust when day is sunday
          const monday = new Date(firstDayOfWeek.setDate(diff))
          const sunday = new Date(monday)
          sunday.setDate(monday.getDate() + 6)

          params.captured_at_start = `${monday.getFullYear()}-${(monday.getMonth() + 1).toString().padStart(2, '0')}-${monday.getDate().toString().padStart(2, '0')} 00:00:00`
          params.captured_at_end = `${sunday.getFullYear()}-${(sunday.getMonth() + 1).toString().padStart(2, '0')}-${sunday.getDate().toString().padStart(2, '0')} 23:59:59`
        }
      }
      console.log('Request params:', params);
      axios.get('http://localhost:5001/api/analysis-projects', { params })
        .then(response => {
          console.log('Backend response:', response.data);
          if (response.data && response.data.length > 0) {
            openProjectDetailDialog(response.data) // 传递整个项目列表
            console.log('openProjectDetailDialog called with data:', response.data);
          } else {
            ElMessage.info('没有找到相关项目。')
            console.log('No relevant projects found.');
          }
        })
        .catch(error => {
          console.error('获取分析项目失败:', error)
          ElMessage.error('获取分析项目失败: ' + (error.response && error.response.data && error.response.data.error || error.message))
        })
    }


    onMounted(() => {
      initCharts()
      initDateOptions()
      // 监听窗口大小变化，重新渲染图表
      window.addEventListener('resize', () => {
        if (languageChart) languageChart.resize()
        if (starsChart) starsChart.resize()
        if (timeChart) timeChart.resize()
      })
    })
    
    onUnmounted(() => {
      // 销毁图表实例，防止内存泄漏
      if (languageChart) {
        languageChart.dispose()
      }
      if (starsChart) {
        starsChart.dispose()
      }
      if (timeChart) {
        timeChart.dispose()
      }
      window.removeEventListener('resize', () => {
        if (languageChart) languageChart.resize()
        if (starsChart) starsChart.resize()
        if (timeChart) timeChart.resize()
      })
    })
    
    watch(analysisType, () => {
      initDateOptions()
    })

    return {
      analysisType,
      selectedDate,
      dateOptions,
      languageChartRef,
      starsChartRef,
      timeChartRef,
      handleTypeChange,
      handleDateChange,
      showProjectDetailDialog,
      selectedProject,
      closeProjectDetailDialog,
      fetchProjectsAndShowDialog // 暴露给模板
    }
  }
}
</script>

<style scoped>
.data-analysis {
  padding: 0 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.charts-container {
  margin-top: 20px;
}

.chart-card {
  height: 400px; /* 固定卡片高度 */
}

.chart {
  width: 100%;
  height: 300px; /* 固定图表高度 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<ProjectDetailDialog :showDialog="showProjectDetailDialog" :projects="selectedProject" @close="closeProjectDetailDialog"/>
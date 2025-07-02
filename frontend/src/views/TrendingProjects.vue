<template>
  <div class="trending-projects">
    <h2>热门项目</h2>
    
    <!-- 项目类型选择 -->
    <el-card class="filter-card">
      <div class="filter-section">
        <el-radio-group v-model="projectType" @change="handleTypeChange">
          <el-radio-button label="daily">每日热门项目</el-radio-button>
          <el-radio-button label="weekly">每周热门项目</el-radio-button>
        </el-radio-group>
        
        <el-select v-model="selectedDate" placeholder="选择日期" @change="handleDateChange">
          <el-option
            v-for="item in dateOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        
        <el-select v-model="languageFilter" placeholder="编程语言" clearable @change="filterProjects">
          <el-option
            v-for="item in languageOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </div>
    </el-card>
    
    <!-- 项目列表 -->
    <el-card class="projects-card">
      <template #header>
        <div class="card-header">
          <span>{{ projectType === 'daily' ? '每日' : '每周' }}热门项目列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索项目"
              prefix-icon="Search"
              clearable
              @input="filterProjects"
              style="width: 200px;"
            />
            <el-select v-model="sortBy" placeholder="排序方式" @change="sortProjects">
              <el-option label="星标数量 (高到低)" value="stars-desc" />
              <el-option label="星标数量 (低到高)" value="stars-asc" />
              <el-option label="最近更新" value="updated" />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table
        :data="displayProjects"
        style="width: 100%"
        :default-sort="{prop: 'stars', order: 'descending'}"
      >
        <el-table-column label="项目名称" min-width="200">
          <template #default="scope">
            <div class="project-name">
              <el-avatar :size="30" :src="scope.row.avatar" />
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
        
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button text type="primary" @click="viewProjectDetails(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 项目详情对话框 -->

    <ProjectDetailDialog
      :showDialog="dialogVisible"
      :project="selectedProject"
      @close="dialogVisible = true"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
// import { Star, Share } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import ProjectDetailDialog from '../components/ProjectDetailDialog.vue'

export default {
  name: 'TrendingProjects',
  components: {

    ProjectDetailDialog
  },
  setup() {
    const projectType = ref('daily')
    const selectedDate = ref('')
    const dateOptions = ref([])
    const languageFilter = ref('')
    const languageOptions = ref([]) // 修改：初始化为空数组，从后端获取
    const searchKeyword = ref('')
    const sortBy = ref('stars-desc')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const dialogVisible = ref(false)
    const selectedProject = ref(null)
    const total = ref(0) // 将 total 移到 setup 函数的顶部

    // 所有项目数据，现在直接从后端获取，不再需要前端过滤和分页
    const allProjects = ref([])

    // 过滤后的项目 (此计算属性将不再用于前端过滤，而是直接显示从后端获取的数据)
    // 仅用于展示，实际过滤和分页由后端完成
    const displayProjects = computed(() => {
      return allProjects.value
    })

    // 初始化日期选项
    const initDateOptions = async () => {
      try {
        const response = await axios.get(`http://localhost:5001/api/trending/dates?type=${projectType.value}`)
        dateOptions.value = response.data.map(date => ({
          label: date,
          value: date
        }))

        if (dateOptions.value.length > 0) {
          selectedDate.value = dateOptions.value[0].value
          await fetchLanguages() // 获取语言选项
          await fetchProjects() // 获取项目数据
        } else {
          selectedDate.value = ''
          languageOptions.value = []
          allProjects.value = []
          total.value = 0
        }
      } catch (error) {
        console.error('获取日期列表失败:', error)
        ElMessage.error('获取日期列表失败')
      }
    }

    // 新增：获取语言选项
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`http://localhost:5001/api/trending/languages?type=${projectType.value}&date=${selectedDate.value}`)
        languageOptions.value = response.data
      } catch (error) {
        console.error('获取语言列表失败:', error)
        ElMessage.error('获取语言列表失败')
      }
    }

    // 获取项目数据
    const fetchProjects = async () => {
      try {
        if (!selectedDate.value) {
          allProjects.value = []
          total.value = 0
          return
        }

        const response = await axios.get(`http://localhost:5001/api/trending`, {
          params: {
            type: projectType.value,
            date: selectedDate.value,
            language: languageFilter.value,
            search: searchKeyword.value, // 添加搜索关键词参数
            sort_by: sortBy.value, // 添加排序参数
            page: currentPage.value,
            per_page: pageSize.value
          }
        })

        if (response.data && response.data.data) {
          allProjects.value = response.data.data.map(item => ({
            id: item.id,
            name: item.name,
            description: item.description || '',
            language: item.language || 'Unknown',
            stars: item.stars || 0,
            forks: item.forks || 0,
            todayStars: item.todayStars || 0,
            url: item.url || '#',
            avatar: item.avatar || `https://github.com/${item.name.split('/')[0]}.png`,
            capturedAt: item.capturedAt || '',
            updatedAt: item.updatedAt || '',
            license: item.license || '未指定'
          }))
          total.value = response.data.total
        } else {
          allProjects.value = []
          total.value = 0
        }
      } catch (error) {
        console.error('获取项目数据失败:', error)
        ElMessage.error('获取项目数据失败')
      }
    }

    // 删除 generateMockData 方法，因为它未被使用
    // const generateMockData = () => {
    //   const mockProjects = []
    //   const languages = ['JavaScript', 'Python', 'Go', 'Rust', 'TypeScript', 'Java', 'C++', 'PHP']
      
    //   for (let i = 1; i <= 50; i++) {
    //     const language = languages[Math.floor(Math.random() * languages.length)]
    //     const stars = Math.floor(Math.random() * 50000) + 1000
    //     const forks = Math.floor(stars * 0.3)
    //     const todayStars = Math.floor(Math.random() * 500) + 50
        
    //     mockProjects.push({
    //       id: i,
    //       name: `awesome-project-${i}`,
    //       description: `这是一个很棒的${language}项目，提供了许多有用的功能和工具。`,
    //       language,
    //       stars,
    //       forks,
    //       todayStars,
    //       url: 'https://github.com/example/awesome-project',
    //       avatar: `https://picsum.photos/seed/${i}/200`,
    //       createdAt: '2024-01-15',
    //       updatedAt: '2025-03-01',
    //       license: 'MIT',
    //       contributors: Array(5).fill().map((_, idx) => ({
    //         name: `contributor-${idx}`,
    //         avatar: `https://picsum.photos/seed/${i}-${idx}/200`
    //       }))
    //     })
    //   }
      
    //   allProjects.value = mockProjects
    // }

    // 处理项目类型变更
    const handleTypeChange = async () => {
      currentPage.value = 1
      languageFilter.value = '' // 重置语言筛选
      searchKeyword.value = '' // 重置搜索关键词
      sortBy.value = 'stars-desc' // 重置排序
      await initDateOptions() // 重新初始化日期选项和数据
    }

    // 处理日期变更
    const handleDateChange = async () => {
      currentPage.value = 1
      languageFilter.value = '' // 重置语言筛选
      searchKeyword.value = '' // 重置搜索关键词
      sortBy.value = 'stars-desc' // 重置排序
      await fetchLanguages() // 重新获取语言选项
      await fetchProjects() // 重新获取项目数据
    }

    // 过滤项目 (现在由后端处理，前端只需触发fetchProjects)
    const filterProjects = () => {
      currentPage.value = 1
      fetchProjects()
    }

    // 排序项目 (现在由后端处理，前端只需触发fetchProjects)
    const sortProjects = () => {
      currentPage.value = 1
      fetchProjects()
    }

    // 添加分页处理方法
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchProjects()
    }

    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchProjects()
    }

    // 查看项目详情
    const viewProjectDetails = (project) => {
      selectedProject.value = project
      dialogVisible.value = true
      console.log('viewProjectDetails called with:', project);
      console.log('dialogVisible:', dialogVisible.value);
    }

    onMounted(() => {
      initDateOptions()
    })

    return {
      projectType,
      selectedDate,
      dateOptions,
      languageFilter,
      languageOptions,
      searchKeyword,
      sortBy,
      currentPage,
      pageSize,
      dialogVisible,
      selectedProject,
      // allProjects, // allProjects 不再需要暴露，因为 displayProjects 已经处理了
      // filteredProjects, // filteredProjects 不再需要暴露
      displayProjects,
      total,
      handleTypeChange,
      handleDateChange,
      filterProjects,
      sortProjects,
      handleSizeChange,
      handleCurrentChange,
      viewProjectDetails
    }
  }
}
</script>

<style scoped>
.trending-projects {
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

.projects-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.project-name {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.project-info {
  display: flex;
  flex-direction: column;
}

.project-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: bold;
}

.project-link:hover {
  text-decoration: underline;
}

.project-desc {
  color: #606266;
  font-size: 12px;
  margin-top: 5px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.today-stars {
  color: #67C23A;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 项目详情样式 */
.project-details {
  padding: 0 20px;
}

.project-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.project-title {
  flex: 1;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 5px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.description {
  margin-bottom: 20px;
  line-height: 1.6;
}

.stats-section, .contributors-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
}

.contributors-list {
  display: flex;
  gap: 10px;
}
</style>
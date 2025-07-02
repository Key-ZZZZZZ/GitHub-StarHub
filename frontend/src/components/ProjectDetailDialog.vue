<template>
  <el-dialog
    :model-value="props.showDialog"
    title="项目详情"
    width="60%"
    @close="handleClose"
  >
    <div v-if="props.projects && props.projects.length > 0">
      <div v-for="project in props.projects" :key="project.url" class="project-item">
        <p><strong>名称:</strong> {{ project.name }}</p>
        <p><strong>作者:</strong> {{ project.author }}</p>
        <p><strong>描述:</strong> {{ project.description }}</p>
        <p><strong>语言:</strong> {{ project.language }}</p>
        <p><strong>星标数:</strong> {{ project.stars }}</p>
        <p><strong>捕获时间:</strong> {{ project.capturedAt }}</p>
        <p><strong>URL:</strong> <a :href="project.url" target="_blank">{{ project.url }}</a></p>
        <el-divider />
      </div>
    </div>
    <div v-else>
      <p>没有项目详情可显示。</p>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { ElDialog, ElButton, ElDivider } from 'element-plus'

const props = defineProps({
  showDialog: {
    type: Boolean,
    default: false
  },
  projects: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.project-item {
  margin-bottom: 10px;
}
.dialog-footer button:first-child {
  margin-right: 10px;
}
</style>
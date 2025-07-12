<template>
  <div class="dashboard-widget">
    <v-card :flat="!props.config?.attrs?.border" :loading="loading" class="fill-height d-flex flex-column">
      <v-card-item v-if="props.config?.attrs?.title || props.config?.attrs?.subtitle">
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-server" class="mr-2" color="primary"></v-icon>
          {{ props.config?.attrs?.title || 'PVE虚拟机守护神概览' }}
        </v-card-title>
        <v-card-subtitle v-if="props.config?.attrs?.subtitle">{{ props.config.attrs.subtitle }}</v-card-subtitle>
      </v-card-item>

      <v-card-text class="flex-grow-1 pa-3">
        <div v-if="loading && !initialDataLoaded" class="text-center py-2">
          <v-progress-circular indeterminate color="primary" size="small"></v-progress-circular>
          <div class="text-caption mt-2">加载中...</div>
        </div>
        <div v-else-if="error" class="text-error text-caption d-flex align-center">
          <v-icon size="small" color="error" class="mr-2">mdi-alert-circle-outline</v-icon>
          {{ error || '数据加载失败' }}
        </div>
        <div v-else-if="initialDataLoaded && summaryData">
          <v-list density="compact" class="py-0" nav>
            <v-list-item class="px-2">
              <template v-slot:prepend>
                <v-icon size="small" :color="summaryData.enabled ? 'success' : 'grey'" class="mr-2">
                  mdi-power
                </v-icon>
              </template>
              <v-list-item-title class="text-caption">
                PVE状态: 
                <span :class="summaryData.enabled ? 'text-success' : 'text-grey'">
                  {{ summaryData.enabled ? '已启用' : '已禁用' }}
                </span>
              </v-list-item-title>
            </v-list-item>

            <v-divider class="my-1"></v-divider>

            <v-list-item class="px-2">
              <template v-slot:prepend>
                <v-icon size="small" :color="summaryData.backup_activity === '空闲' ? 'success' : 'warning'" class="mr-2">
                  mdi-database-arrow-up
                </v-icon>
              </template>
              <v-list-item-title class="text-caption">
                备份状态: 
                <span :class="summaryData.backup_activity === '空闲' ? 'text-success' : 'text-warning'">
                  {{ summaryData.backup_activity || '空闲' }}
                </span>
              </v-list-item-title>
            </v-list-item>
            
            <v-list-item class="px-2">
              <template v-slot:prepend>
                <v-icon size="small" :color="summaryData.restore_activity === '空闲' ? 'success' : 'warning'" class="mr-2">
                  mdi-database-arrow-down
                </v-icon>
              </template>
              <v-list-item-title class="text-caption">
                恢复状态: 
                <span :class="summaryData.restore_activity === '空闲' ? 'text-success' : 'text-warning'">
                  {{ summaryData.restore_activity || '空闲' }}
                </span>
              </v-list-item-title>
            </v-list-item>
            
            <v-list-item class="px-2">
              <template v-slot:prepend>
                <v-icon size="small" color="info" class="mr-2">mdi-archive</v-icon>
              </template>
              <v-list-item-title class="text-caption">
                可用备份: {{ summaryData.available_backups || 0 }} 个文件
              </v-list-item-title>
            </v-list-item>
            
            <v-list-item class="px-2" v-if="summaryData.enabled">
              <template v-slot:prepend>
                <v-icon size="small" color="amber-darken-2" class="mr-2">mdi-timer-outline</v-icon>
              </template>
              <v-list-item-title class="text-caption">
                下次备份: {{ summaryData.next_run_time || '未知' }}
              </v-list-item-title>
            </v-list-item>
            
            <v-list-item class="px-2">
              <template v-slot:prepend>
                <v-icon size="small" color="deep-purple" class="mr-2">mdi-lan-connect</v-icon>
              </template>
              <v-list-item-title class="text-caption">
                PVE主机: {{ summaryData.pve_host || '未配置' }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </div>
        <div v-else class="text-caption text-disabled text-center py-3">
          <v-icon icon="mdi-information-outline" class="mb-2"></v-icon>
          <div>暂无数据，请检查PVE虚拟机守护神配置</div>
        </div>
      </v-card-text>

      <v-divider v-if="props.allowRefresh"></v-divider>
      <v-card-actions v-if="props.allowRefresh" class="px-3 py-1">
        <span class="text-caption text-disabled">{{ lastRefreshedTimeDisplay }}</span>
        <v-spacer></v-spacer>
        <v-btn icon variant="text" size="small" @click="fetchSummary" :loading="loading">
          <v-icon size="small">mdi-refresh</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';

const props = defineProps({
  api: { 
    type: Object,
    required: true,
  },
  config: { // Widget display config (title, border etc.)
    type: Object,
    default: () => ({ attrs: {} }),
  },
  allowRefresh: {
    type: Boolean,
    default: false,
  },
  refreshInterval: {
    type: Number,
    default: 0, // 0 means no auto-refresh
  },
});

const loading = ref(false);
const error = ref(null);
const initialDataLoaded = ref(false);
const summaryData = reactive({ 
    enabled: null,
    pve_host: null,
    backup_activity: null,
    restore_activity: null,
    available_backups: 0,
    next_run_time: null,
});
const lastRefreshedTimestamp = ref(null);

let refreshTimer = null;

const getPluginId = () => {
  return "ProxmoxVEBackup";
};

async function fetchSummary() {
  loading.value = true;
  error.value = null;
  
  try {
    const pluginId = getPluginId();
    const statusData = await props.api.get(`plugin/ProxmoxVEBackup/status`);
    const filesData = await props.api.get(`plugin/ProxmoxVEBackup/available_backups`);
    
    if (statusData) {
      // 更新状态数据
      summaryData.enabled = statusData.enabled;
      summaryData.pve_host = statusData.pve_host;
      summaryData.backup_activity = statusData.backup_activity;
      summaryData.restore_activity = statusData.restore_activity;
      summaryData.next_run_time = statusData.next_run_time;
      
      // 更新备份文件数量
      if (filesData && Array.isArray(filesData)) {
        summaryData.available_backups = filesData.length;
      } else {
        summaryData.available_backups = 0;
      }
      
      initialDataLoaded.value = true;
      lastRefreshedTimestamp.value = Date.now();
    } else {
      throw new Error('仪表盘数据响应无效');
    }
  } catch (err) {
    error.value = err.message || '获取仪表盘数据失败';
  } finally {
    loading.value = false;
  }
}

const lastRefreshedTimeDisplay = computed(() => {
  if (!lastRefreshedTimestamp.value) return '';
  return `上次更新: ${new Date(lastRefreshedTimestamp.value).toLocaleTimeString()}`;
});

onMounted(() => {
  fetchSummary();
  
  // 设置自动刷新
  if (props.allowRefresh && props.refreshInterval > 0) {
    refreshTimer = setInterval(fetchSummary, props.refreshInterval * 1000);
  }
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});
</script>

<style scoped>
.dashboard-widget {
  height: 100%;
  width: 100%;
}
.v-card-item {
  padding-bottom: 8px;
}
.v-list-item {
  min-height: 28px;
}
</style>

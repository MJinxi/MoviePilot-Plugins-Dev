<template>
  <v-card flat class="gallery-page">
    <!-- 顶部标题栏 -->
    <v-card-title class="section-title d-flex align-center mb-4">
      <v-icon class="mr-2" color="primary" size="28">mdi-image-multiple</v-icon>
      <span class="text-h5 font-weight-bold">随机图库状态</span>
      <v-spacer />
      <v-btn
        v-if="isMobile"
        icon
        class="close-btn"
        @click="$emit('close')"
      >
        <v-icon size="28" color="grey">mdi-close</v-icon>
      </v-btn>
    </v-card-title>

    <!-- 状态概览卡片 -->
    <v-row class="mb-6" align="stretch" dense>
      <!-- 服务状态 -->
      <v-col cols="12" md="3">
        <v-card class="glass-card" elevation="4">
          <v-card-title class="d-flex align-center">
            <v-icon :color="status.server_status === 'running' ? 'success' : 'grey'" size="24" class="mr-2">
              {{ status.server_status === 'running' ? 'mdi-server-network' : 'mdi-server-off' }}
            </v-icon>
            <span>服务状态</span>
            <v-spacer />
            <v-btn icon size="small" @click="refreshStatus" :loading="refreshing">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div class="status-item">
              <span class="label font-weight-bold">运行状态：</span>
              <v-chip
                :color="status.server_status === 'running' ? 'success' : 'grey'"
                size="small"
                class="ml-1"
                variant="elevated"
              >
                {{ status.server_status === 'running' ? '已启用' : '已禁用' }}
              </v-chip>
            </div>
            <div class="status-item">
              <span class="label font-weight-bold">服务端口：</span>
              <v-chip color="primary" size="small" class="ml-1" variant="elevated">{{ status.port || '未配置' }}</v-chip>
            </div>
            <div class="status-item">
              <span class="label font-weight-bold">服务监听IP：</span>
              <v-chip color="info" size="small" class="ml-1" variant="elevated">{{ currentHost || '-' }}</v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 目录监控 -->
      <v-col cols="12" md="3">
        <v-card class="glass-card" elevation="4">
          <v-card-title class="d-flex align-center">
            <v-icon color="info" size="24" class="mr-2">mdi-folder-check</v-icon>
            <span>目录监控</span>
          </v-card-title>
          <v-card-text>
            <div class="status-item">
              <span class="label">横屏目录：</span>
              <v-chip :color="(status.pc_path || status.network_image_url_pc) ? 'success' : 'error'" size="small">
                {{ (status.pc_path || status.network_image_url_pc) ? '已配置' : '未配置' }}
              </v-chip>
            </div>
            <div class="status-item">
              <span class="label">竖屏目录：</span>
              <v-chip :color="(status.mobile_path || status.network_image_url_mobile) ? 'success' : 'error'" size="small">
                {{ (status.mobile_path || status.network_image_url_mobile) ? '已配置' : '未配置' }}
              </v-chip>
            </div>
            <div class="status-item">
              <span class="label">配置完整性：</span>
              <v-chip :color="status.pc_path && status.mobile_path ? 'success' : 'warning'" size="small">
                {{ status.pc_path && status.mobile_path ? '完整' : '不完整' }}
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 图片统计 -->
      <v-col cols="12" md="3">
        <v-card class="glass-card" elevation="4">
          <v-card-title class="d-flex align-center">
            <v-icon color="info" size="24" class="mr-2">mdi-image</v-icon>
            <span>图片统计</span>
          </v-card-title>
          <v-card-text>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">
                  <span v-if="!status.pc_path && status.network_image_url_pc || !status.mobile_path && status.network_image_url_mobile">未知</span>
                  <span v-else>{{ status.total_count }}</span>
                </div>
                <div class="stat-label">总图片数</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">
                  <span v-if="!status.pc_path && status.network_image_url_pc">未知</span>
                  <span v-else>{{ status.pc_count }}</span>
                </div>
                <div class="stat-label">横屏图片</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">
                  <span v-if="!status.mobile_path && status.network_image_url_mobile">未知</span>
                  <span v-else>{{ status.mobile_count }}</span>
                </div>
                <div class="stat-label">竖屏图片</div>
              </div>
              <div class="stat-item">
                <div class="stat-number" style="color:#ff9800;">{{ status.today_visits }}</div>
                <div class="stat-label">今日访问</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 快速操作 -->
      <v-col cols="12" md="3">
        <v-card class="glass-card" elevation="4">
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" size="24" class="mr-2">mdi-lightning-bolt</v-icon>
            <span>快速操作</span>
          </v-card-title>
          <v-card-text>
            <div class="action-buttons">
              <v-btn
                color="info"
                size="small"
                prepend-icon="mdi-cog"
                @click="$emit('switch')"
                class="action-btn"
              >
                插件配置
              </v-btn>
              <v-btn
                color="warning"
                size="small"
                prepend-icon="mdi-restart"
                @click="startService"
                :loading="starting"
                class="action-btn"
              >
                重启服务
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 图片预览区域 -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card class="glass-card" elevation="4">
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" size="24" class="mr-2">mdi-image-search</v-icon>
            <span>图片预览</span>
            <v-spacer />
            <v-btn-group>
              <v-btn
                size="small"
                :color="previewType === 'pc' ? 'primary' : 'grey'"
                @click="previewType = 'pc'"
              >
                横屏
              </v-btn>
              <v-btn
                size="small"
                :color="previewType === 'mobile' ? 'primary' : 'grey'"
                @click="previewType = 'mobile'"
              >
                竖屏
              </v-btn>
              <v-btn
                size="small"
                :color="previewType === 'auto' ? 'primary' : 'grey'"
                @click="previewType = 'auto'"
              >
                自动
              </v-btn>
            </v-btn-group>
            <v-btn
              color="primary"
              size="small"
              class="ml-4 btn-gradient-refresh"
              prepend-icon="mdi-refresh"
              @click="loadPreview"
              :loading="previewLoading"
            >
              刷新预览
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div class="preview-container">
              <div v-if="previewLoading && !previewImageUrl" class="preview-loading">
                <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
                <div class="mt-4">正在加载图片...</div>
              </div>
              <div v-else-if="previewError" class="preview-error">
                <v-icon color="error" size="64">mdi-image-broken</v-icon>
                <div class="mt-4 text-error">{{ previewError }}</div>
                <v-btn color="primary" @click="loadPreview" class="mt-4">重试</v-btn>
              </div>
              <div v-else class="preview-image-container">
                <img
                  v-if="previewImageUrl"
                  :src="previewImageUrl"
                  :alt="'随机图片预览 - ' + previewType"
                  class="preview-image"
                  @load="previewLoading = false"
                  @error="handlePreviewError"
                />
                <div v-else class="preview-placeholder">
                  <v-icon color="grey" size="64">mdi-image</v-icon>
                  <div class="mt-4 text-grey">点击下方按钮预览图片</div>
                </div>
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="preview-actions">
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- API 接口信息 -->
    <v-row class="mb-6 api-row">
      <v-col cols="12">
        <v-card class="glass-card" elevation="4">
          <v-card-title class="d-flex align-center">
            <v-icon color="success" size="24" class="mr-2">mdi-api</v-icon>
            <span>API 接口</span>
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <div class="api-endpoint">
                  <div class="endpoint-title">
                    <v-icon color="primary" size="20" class="mr-2">mdi-web</v-icon>
                    <span class="api-title">自动识别设备</span>
                  </div>
                  <div class="api-url">{{ getApiUrl('/random') }}</div>
                  <div class="endpoint-desc">根据设备类型自动返回横屏或竖屏图片</div>
                </div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="api-endpoint">
                  <div class="endpoint-title">
                    <v-icon color="success" size="20" class="mr-2">mdi-monitor</v-icon>
                    <span class="api-title">指定横屏图片</span>
                  </div>
                  <div class="api-url">{{ getApiUrl('/random?type=pc') }}</div>
                  <div class="endpoint-desc">强制返回横屏图片</div>
                </div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="api-endpoint">
                  <div class="endpoint-title">
                    <v-icon color="warning" size="20" class="mr-2">mdi-cellphone</v-icon>
                    <span class="api-title">指定竖屏图片</span>
                  </div>
                  <div class="api-url">{{ getApiUrl('/random?type=mobile') }}</div>
                  <div class="endpoint-desc">强制返回竖屏图片</div>
                </div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="api-endpoint">
                  <div class="endpoint-title">
                    <v-icon color="info" size="20" class="mr-2">mdi-chart-bar</v-icon>
                    <span class="api-title">统计数据</span>
                  </div>
                  <div class="api-url">{{ getApiUrl('/stats') }}</div>
                  <div class="endpoint-desc">获取图片数量和访问统计</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 更紧凑的底部操作栏 -->
    <v-divider></v-divider>

    <!-- 通知 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout">
      {{ snackbar.text }}
    </v-snackbar>
  </v-card>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
const currentHost = window.location.hostname;

const props = defineProps({
  api: { type: Object, required: true }
});

const emit = defineEmits(['close', 'switch']);

// 响应式数据
const status = reactive({
  enabled: false,
  port: "",
  pc_path: "",
  mobile_path: "",
  pc_count: 0,
  mobile_count: 0,
  total_count: 0,
  today_visits: 0,
  server_status: "stopped",
  last_error: "",
  listen_ip: "",
  network_image_url_pc: "",
  network_image_url_mobile: "",
});

// 新增：详细统计
const statusDetail = ref({
  local: { pc: 0, mobile: 0 },
  network: { pc: 0, mobile: 0 }
});

const previewType = ref('auto');
const previewImageUrl = ref('');
const previewLoading = ref(false);
const previewError = ref('');

const refreshing = ref(false);
const starting = ref(false);
const stopping = ref(false);

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
});

// 计算属性
const isMobile = computed(() => {
  return window.innerWidth < 768;
});

// 方法
const showNotification = (text, color = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
};

function getAccessibleIp() {
  const ip = status.listen_ip || 'localhost';
  // 如果 listen_ip 是 127.0.0.1、localhost 或 172.开头（docker bridge），用当前页面的 hostname
  if (
    ip === '127.0.0.1' ||
    ip === 'localhost' ||
    ip.startsWith('172.')
  ) {
    return window.location.hostname;
  }
  return ip;
}

const getApiUrl = (endpoint) => {
  const ip = getAccessibleIp();
  const port = status.port || '8002';
  return `http://${ip}:${port}${endpoint}`;
};

const getVisitProgress = () => {
  // 模拟访问进度，基于今日访问量
  return Math.min((status.today_visits / 100) * 100, 100);
};

const refreshStatus = async () => {
  refreshing.value = true;
  try {
    const statusData = await props.api.get('plugin/RandomPic/status');
    Object.assign(status, statusData);
    if (statusData.detail) {
      statusDetail.value = statusData.detail;
    }
    showNotification('状态已刷新', 'success');
  } catch (error) {
    showNotification('刷新状态失败', 'error');
  } finally {
    refreshing.value = false;
  }
};

const loadPreview = async () => {
  if (status.server_status !== 'running' || !status.port) {
    previewError.value = '服务未启动或端口未配置';
    previewLoading.value = false;
    return;
  }
  previewLoading.value = true;
  previewError.value = '';
  try {
    const ip = getAccessibleIp();
    let url = `http://${ip}:${status.port}/random`;
    if (previewType.value !== 'auto') {
      url += `?type=${previewType.value}`;
    }
    url += (url.includes('?') ? '&' : '?') + `t=${Date.now()}`;
    // 先用 new Image() 预加载
    const img = new window.Image();
    img.onload = () => {
      previewImageUrl.value = url;
      previewLoading.value = false;
    };
    img.onerror = () => {
      previewError.value = '图片加载失败';
      previewLoading.value = false;
    };
    img.src = url;
  } catch (error) {
    previewError.value = '加载预览失败';
    previewLoading.value = false;
    showNotification('加载预览失败', 'error');
  }
};

const handlePreviewError = () => {
  previewLoading.value = false;
  previewError.value = '图片加载失败';
};

const previewRandom = () => {
  loadPreview();
};

const openWebPreview = () => {
  if (!status.port) {
    showNotification('端口未配置', 'error');
    return;
  }
  const ip = getAccessibleIp();
  window.open(`http://${ip}:${status.port}/preview`, '_blank');
};

const downloadPreview = () => {
  // 直接取页面上 img 的 src，保证和显示一致
  const img = document.querySelector('.preview-image');
  if (!img || !img.src) return;
  const link = document.createElement('a');
  link.href = img.src;
  link.download = `random-image-${Date.now()}.jpg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showNotification('图片下载已开始', 'success');
};

const openPreviewInNewTab = () => {
  const img = document.querySelector('.preview-image');
  if (!img || !img.src) return;
  window.open(img.src, '_blank');
};

const startService = async () => {
  starting.value = true;
  try {
    // 通过API获取当前配置
    const config = await props.api.get('plugin/RandomPic/config');
    config.enable = true;
    await props.api.post('plugin/RandomPic/config', config);
    await refreshStatus();
    showNotification('服务已启动', 'success');
  } catch (error) {
    showNotification('启动服务失败', 'error');
  } finally {
    starting.value = false;
  }
};

const stopService = async () => {
  stopping.value = true;
  try {
    // 通过API获取当前配置
    const config = await props.api.get('plugin/RandomPic/config');
    config.enable = false;
    await props.api.post('plugin/RandomPic/config', config);
    await refreshStatus();
    showNotification('服务已停止', 'success');
  } catch (error) {
    showNotification('停止服务失败', 'error');
  } finally {
    stopping.value = false;
  }
};

const refreshAll = async () => {
  await refreshStatus();
  if (status.enabled) {
    loadPreview();
  }
};

// 生命周期
onMounted(async () => {
  await refreshStatus();
  loadPreview();
});
</script>

<style scoped>
.gallery-page {
  padding: 24px;
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  border-radius: 24px;
  padding-bottom: 0 !important;
}
.v-card:last-child {
  margin-bottom: 0 !important;
}
.theme-light .gallery-page {
  background: rgba(255,255,255,0.92) !important;
  border: 2px solid #42a5f5;
  box-shadow: 0 8px 32px 0 #90caf9cc, 0 2px 12px 0 #1976d244;
}
.theme-dark .gallery-page {
  background: rgba(40,50,70,0.75) !important;
  border: 2px solid #00eaff77;
  box-shadow: 0 0 32px 0 #00eaff33;
}

.glass-card, .footer-actions {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
}

.section-title {
  color: #1976d2;
  font-weight: 600;
  padding: 16px 0;
}

/* 玻璃拟态卡片样式，直接用 proxmoxvebackup 的 glass-card */
.glass-card {
  background: rgba(40, 50, 70, 0.75);
  border-radius: 18px;
  box-shadow: 0 4px 32px 0 #00eaff22, 0 1.5px 8px 0 #0006;
  backdrop-filter: blur(8px);
  border: 1.5px solid #00eaff33;
  margin-bottom: 2px;
  padding: 24px 32px 16px 32px;
  min-height: 180px;
}

/* 删除所有 status-card、server-status、image-stats、dir-status、quick-actions、api-card、preview-card、api-bg-*、api-endpoint 的背景色、渐变色等自定义样式，只保留必要的布局和字体色 */

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.status-item .label {
  font-weight: 500;
  color: #666;
}
.status-item .value {
  font-weight: 600;
  color: #333;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  min-height: 96px;
  align-items: center;
}
.stat-item {
  text-align: center;
  padding: 0;
  margin: 0;
}
.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #1976d2;
}
.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.action-btn {
  width: 100%;
}
.preview-container {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
}
.preview-loading,
.preview-error,
.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #666;
}
.preview-image-container {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.preview-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.api-endpoint {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.endpoint-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 8px;
}
.api-title {
  font-weight: 600;
  font-size: 16px;
  color: #1976d2;
}
.api-url {
  font-family: 'Courier New', monospace;
  background: none;
  padding: 8px 12px;
  border-radius: 4px;
  color: #1976d2;
  font-size: 15px;
  margin: 10px 0 8px 0;
  word-break: break-all;
  user-select: all;
}
.endpoint-desc {
  font-size: 13px;
  color: #888;
}
.footer-actions {
  background: transparent;
  box-shadow: none;
  border-radius: 12px;
  margin-top: 16px;
  padding: 16px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  .action-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .action-btn {
    width: auto;
    flex: 1;
  }
  .preview-actions {
    flex-direction: column;
  }
  .footer-actions {
    flex-direction: column;
    gap: 8px;
  }
}
/* 美化刷新预览按钮 */
.btn-gradient-refresh {
  background: linear-gradient(90deg, #42a5f5 0%, #7e57c2 100%) !important;
  color: #fff !important;
  border-radius: 8px;
  font-weight: 500;
  min-width: 90px;
  height: 36px;
  font-size: 15px;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px 0 #42a5f533;
  border: none;
  padding: 0 18px;
  transition: box-shadow 0.2s, background 0.2s, transform 0.12s;
}
.btn-gradient-refresh:hover {
  background: linear-gradient(90deg, #7e57c2 0%, #42a5f5 100%) !important;
  box-shadow: 0 4px 16px 0 #7e57c244;
  transform: translateY(-1px) scale(1.03);
}
.btn-gradient-refresh:active {
  box-shadow: 0 1px 4px 0 #42a5f522;
  transform: scale(0.98);
}

.btn-gradient-start {
  background: linear-gradient(90deg, #00e676 0%, #00bcd4 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px 0 #00e67655;
  border-radius: 10px;
  font-weight: 500;
  min-width: 120px;
}
.btn-gradient-start:hover {
  background: linear-gradient(90deg, #00bcd4 0%, #00e676 100%) !important;
}

.btn-gradient-stop {
  background: linear-gradient(90deg, #e040fb 0%, #ff4081 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px 0 #e040fb55;
  border-radius: 10px;
  font-weight: 500;
  min-width: 120px;
}
.btn-gradient-stop:hover {
  background: linear-gradient(90deg, #ff4081 0%, #e040fb 100%) !important;
}
</style> 
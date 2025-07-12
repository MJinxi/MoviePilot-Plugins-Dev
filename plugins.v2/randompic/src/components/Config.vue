<template>
  <div class="plugin-config">
    <v-card flat class="rounded border">
      <v-card-text>
        <div class="config-header">
          <div class="gallery-visual">
            <div class="floating-images">
              <div class="floating-image img-1" :style="{ transform: `rotate(${imageRotation}deg)` }">
                <v-icon size="32" color="primary">mdi-image</v-icon>
              </div>
              <div class="floating-image img-2" :style="{ transform: `rotate(${-imageRotation}deg)` }">
                <v-icon size="28" color="success">mdi-image-multiple</v-icon>
              </div>
              <div class="floating-image img-3" :style="{ transform: `rotate(${imageRotation * 0.5}deg)` }">
                <v-icon size="24" color="warning">mdi-image-outline</v-icon>
              </div>
            </div>
            <div class="config-title">
              <v-icon size="36" color="primary" class="mr-3">mdi-cog</v-icon>
              <span class="text-h4 font-weight-bold">图库配置</span>
            </div>
            <div class="config-subtitle">配置您的随机图片服务</div>
          </div>
        </div>

        <!-- 基本设置 -->
        <div class="glass-card config-section basic-settings">
          <div class="section-title">
            <v-icon class="mr-2" color="primary">mdi-tune</v-icon>
            基本设置
          </div>
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="config.enable"
                  label="启用插件"
                  color="success"
                  prepend-icon="mdi-power"
                  class="config-switch"
                  @change="onConfigChange"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="config.port"
                  label="服务端口"
                  placeholder="8002"
                  prepend-inner-icon="mdi-numeric"
                  hint=""
                  dense
                  @input="onConfigChange"
                />
                <div class="port-hint" style="font-size:12px;display:flex;align-items:center;margin-top:8px;margin-bottom:0;">
                  <v-icon size="16" color="info" style="margin-right:4px;">mdi-information</v-icon>
                  容器为 bridge 模式需要手动映射配置的端口
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </div>

        <!-- 本地目录配置 -->
        <div class="glass-card config-section local-directory-settings">
          <div class="section-title">
            <v-icon class="mr-2" color="info">mdi-folder-multiple-image</v-icon>
            本地目录配置
          </div>
          <v-card-text>
            <!-- 横屏本地目录 -->
            <v-row dense class="mb-4">
              <v-col cols="12">
                <div class="directory-card pc-directory">
                  <div class="directory-header">
                    <v-icon color="primary" size="24" class="mr-2">mdi-monitor</v-icon>
                    <span class="directory-title">横屏本地图片目录</span>
                    <v-chip color="primary" size="small" class="ml-2">PC/横屏</v-chip>
                  </div>
                  <v-text-field
                    v-model="config.pc_path"
                    label="横屏图片路径"
                    placeholder="/path/pc/images"
                    prepend-inner-icon="mdi-folder"
                    hint=""
                    dense
                    @input="onConfigChange"
                  />
                </div>
              </v-col>
            </v-row>
            <!-- 竖屏本地目录 -->
            <v-row dense>
              <v-col cols="12">
                <div class="directory-card mobile-directory">
                  <div class="directory-header">
                    <v-icon color="success" size="24" class="mr-2">mdi-cellphone</v-icon>
                    <span class="directory-title">竖屏本地图片目录</span>
                    <v-chip color="success" size="small" class="ml-2">Mobile/竖屏</v-chip>
                  </div>
                  <v-text-field
                    v-model="config.mobile_path"
                    label="竖屏图片路径"
                    placeholder="/path/mobile/images"
                    prepend-inner-icon="mdi-folder"
                    hint=""
                    dense
                    @input="onConfigChange"
                  />
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </div>

        <!-- 网络目录配置 -->
        <div class="glass-card config-section network-directory-settings">
          <div class="section-title">
            <v-icon class="mr-2" color="primary">mdi-link-variant</v-icon>
            网络目录配置
          </div>
          <v-card-text>
            <!-- 横屏网络图片地址 -->
            <v-row dense class="mb-4">
              <v-col cols="12">
                <div class="directory-card pc-directory">
                  <div class="directory-header">
                    <v-icon color="primary" size="24" class="mr-2">mdi-monitor</v-icon>
                    <span class="directory-title">横屏网络图片地址</span>
                    <v-chip color="primary" size="small" class="ml-2">PC/横屏</v-chip>
                  </div>
                  <v-text-field
                    v-model="config.network_image_url_pc"
                    label="横屏网络图片地址"
                    placeholder="https://example.com/your-pc-image.jpg，支持多个逗号分隔"
                    prepend-inner-icon="mdi-link"
                    hint="支持图片直链、API、json/txt等，多个用英文逗号分隔，优先级高于本地横屏目录"
                    persistent-hint
                    dense
                    @input="onConfigChange"
                  />
                </div>
              </v-col>
            </v-row>
            <!-- 竖屏网络图片地址 -->
            <v-row dense>
              <v-col cols="12">
                <div class="directory-card mobile-directory">
                  <div class="directory-header">
                    <v-icon color="success" size="24" class="mr-2">mdi-cellphone-link</v-icon>
                    <span class="directory-title">竖屏网络图片地址</span>
                    <v-chip color="success" size="small" class="ml-2">Mobile/竖屏</v-chip>
                  </div>
                  <v-text-field
                    v-model="config.network_image_url_mobile"
                    label="竖屏网络图片地址"
                    placeholder="https://example.com/your-mobile-image.jpg，支持多个逗号分隔"
                    prepend-inner-icon="mdi-link"
                    hint="支持图片直链、API、json/txt等，多个用英文逗号分隔，优先级高于本地竖屏目录"
                    persistent-hint
                    dense
                    @input="onConfigChange"
                  />
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </div>

        <!-- 通知 -->
        <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout">
          {{ snackbar.text }}
        </v-snackbar>
      </v-card-text>
      
      <v-card-actions class="px-2 py-1">
        <v-btn class="btn-gradient-status" @click="$emit('switch')" prepend-icon="mdi-view-dashboard" :disabled="saving" size="small">状态页</v-btn>
        <v-spacer></v-spacer>
        <v-btn class="btn-gradient-reset" @click="resetConfig" :disabled="saving" prepend-icon="mdi-restore" size="small">重置</v-btn>
        <v-btn class="btn-gradient-save" :disabled="!isConfigValid() || saving" @click="saveConfig" :loading="saving" prepend-icon="mdi-content-save" size="small">保存配置</v-btn>
        <v-btn class="btn-gradient-close" @click="$emit('close')" prepend-icon="mdi-close" :disabled="saving" size="small">关闭</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) }
});

const emit = defineEmits(['close', 'switch', 'config-updated-on-server', 'back-to-status']);

// 响应式数据
const config = reactive({
  enable: false,
  port: "8002",
  pc_path: "",
  mobile_path: "",
  network_image_url_pc: "",
  network_image_url_mobile: "",
  network_image_url: "", // 兼容老配置
});

const saving = ref(false);
const imageRotation = ref(0);

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
});

// 计算属性
const isConfigComplete = () => {
  const hasPc = config.pc_path || config.network_image_url_pc;
  const hasMobile = config.mobile_path || config.network_image_url_mobile;
  return config.enable && config.port && hasPc && hasMobile;
};

const isConfigValid = () => {
  const hasPc = config.pc_path || config.network_image_url_pc;
  const hasMobile = config.mobile_path || config.network_image_url_mobile;
  return config.port && hasPc && hasMobile;
};

// 方法
const showNotification = (text, color = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
};

const getServiceStatusColor = () => {
  if (!config.enable) return 'grey';
  if (!isConfigComplete()) return 'warning';
  return 'success';
};

const getServiceStatusIcon = () => {
  if (!config.enable) return 'mdi-server-off';
  if (!isConfigComplete()) return 'mdi-server-alert';
  return 'mdi-server-network';
};

const onConfigChange = () => {
  // 配置变更时的处理
};

const resetConfig = () => {
  Object.assign(config, {
    enable: false,
    port: "8002",
    pc_path: "",
    mobile_path: "",
    network_image_url_pc: "",
    network_image_url_mobile: "",
    network_image_url: "",
  });
  showNotification('配置已重置', 'info');
};

const saveConfig = async () => {
  if (!isConfigValid()) {
    showNotification('请完善配置信息', 'warning');
    return;
  }

  saving.value = true;
  try {
    const result = await props.api.post('plugin/RandomPic/config', config);
    showNotification('配置保存成功', 'success');
    emit('save', JSON.parse(JSON.stringify(config)));
    emit('config-updated-on-server', config);
  } catch (error) {
    showNotification('配置保存失败', 'error');
  } finally {
    saving.value = false;
  }
};

// 生命周期
onMounted(() => {
  // 初始化配置
  if (props.initialConfig) {
    Object.assign(config, props.initialConfig);
  }

  // 启动图片旋转动画
  setInterval(() => {
    imageRotation.value = (imageRotation.value + 1) % 360;
  }, 50);
});
</script>

<style scoped>
.plugin-page, .config-page {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  border-radius: 24px;
  padding: 0;
}
.theme-light .plugin-page, .theme-light .config-page {
  background: rgba(255,255,255,0.92) !important;
  border: 2px solid #42a5f5;
  box-shadow: 0 8px 32px 0 #90caf9cc, 0 2px 12px 0 #1976d244;
}
.theme-dark .plugin-page, .theme-dark .config-page {
  background: rgba(40,50,70,0.75) !important;
  border: 2px solid #00eaff77;
  box-shadow: 0 0 32px 0 #00eaff33;
}

.config-page {
  background: transparent;
}

.config-header {
  margin-bottom: 24px;
}

.gallery-visual {
  position: relative;
  text-align: center;
  padding: 32px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  overflow: hidden;
}

.floating-images {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-image {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease;
}

.floating-image.img-1 {
  top: 20%;
  left: 15%;
  width: 80px;
  height: 80px;
}

.floating-image.img-2 {
  top: 60%;
  right: 20%;
  width: 60px;
  height: 60px;
}

.floating-image.img-3 {
  top: 30%;
  right: 10%;
  width: 40px;
  height: 40px;
}

.config-title {
  color: white;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.config-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  position: relative;
  z-index: 1;
}

.config-section,
.glass-card {
  margin-bottom: 8px !important;
}

/* 玻璃拟态样式 */
.glass-card {
  background: rgba(40, 50, 70, 0.75);
  border-radius: 18px;
  box-shadow: 0 4px 32px 0 #00eaff22, 0 1.5px 8px 0 #0006;
  backdrop-filter: blur(8px);
  border: 1.5px solid #00eaff33;
  margin-bottom: 2px !important;
  padding: 24px 32px 16px 32px;
}
.section-title {
  font-weight: 600;
  font-size: 1.15rem;
  display: flex;
  align-items: center;
  color: #00eaff;
  margin-bottom: 4px;
  letter-spacing: 1px;
  text-shadow: 0 2px 8px #00eaff44;
}

.config-switch {
  margin-bottom: 8px;
}

.directory-card {
  padding: 16px;
  border-radius: 8px;
  border: none;
  background: transparent;
  box-shadow: none;
  transition: all 0.3s ease;
}

.directory-card:hover {
  transform: translateY(-2px);
  box-shadow: none;
}

.pc-directory {
  background: transparent;
  border: none;
}

.mobile-directory {
  background: transparent;
  border: none;
}

.directory-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.directory-title {
  font-weight: 600;
}

.directory-info {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.info-text {
  font-size: 12px;
  color: #666;
}

.status-preview-card {
  padding: 16px;
  border-radius: 8px;
  background: transparent;
  border: none;
  box-shadow: none;
}

.status-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 12px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item .label {
  font-weight: 500;
  color: #666;
}

.status-item .value {
  font-weight: 600;
  color: #333;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.action-btns {
  display: flex;
  justify-content: flex-end;
  gap: 18px;
  margin-top: 24px;
  background: transparent !important;
  box-shadow: none !important;
  border-radius: 12px;
  padding: 0;
}
.glow-btn {
  border-radius: 10px;
  font-weight: 500;
  min-width: 120px;
  background: linear-gradient(90deg, #00eaff 0%, #3f51b5 100%);
  color: #fff !important;
  box-shadow: 0 2px 16px 0 #00eaff55;
  transition: box-shadow 0.3s, background 0.3s;
}
.glow-btn:hover {
  box-shadow: 0 4px 32px 0 #00eaffcc;
  background: linear-gradient(90deg, #3f51b5 0%, #00eaff 100%);
}

.v-alert {
  background: transparent !important;
  box-shadow: none !important;
}

.glass-card.config-section,
.basic-settings,
.directory-settings {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.config-section.usage-info {
  margin-top: 2px !important;
}

.gallery-visual,
.floating-image,
.config-header,
.back-btn-wrapper,
.config-title,
.config-subtitle,
.directory-header,
.directory-info,
.info-text,
.section-title,
.v-card-title,
.v-card-text,
.action-btns,
.preview-url,
.preview-container,
.preview-placeholder,
.preview-loading,
.preview-error,
.preview-image-container {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* 彻底去除底部左下角角块，全局兜底 */
.plugin-page > *,
.plugin-page *::before,
.plugin-page *::after,
.plugin-page::before,
.plugin-page::after {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

@media (max-width: 768px) {
  .action-btns {
    flex-direction: column;
    gap: 10px;
  }
  .glow-btn {
    width: 100%;
    min-width: 0;
    margin: 0;
  }
  
  .floating-image {
    display: none;
  }
  
  .config-title {
    font-size: 24px;
  }
}

.btn-gradient-status {
  background: linear-gradient(90deg, #42a5f5 0%, #7e57c2 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px 0 #42a5f555;
}
.btn-gradient-status:hover {
  background: linear-gradient(90deg, #7e57c2 0%, #42a5f5 100%) !important;
}

.btn-gradient-reset {
  background: linear-gradient(90deg, #ff9800 0%, #f44336 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px 0 #ff980055;
}
.btn-gradient-reset:hover {
  background: linear-gradient(90deg, #f44336 0%, #ff9800 100%) !important;
}

.btn-gradient-save {
  background: linear-gradient(90deg, #00e676 0%, #00bcd4 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px 0 #00e67655;
}
.btn-gradient-save:hover {
  background: linear-gradient(90deg, #00bcd4 0%, #00e676 100%) !important;
}

.btn-gradient-close {
  background: linear-gradient(90deg, #e040fb 0%, #ff4081 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px 0 #e040fb55;
}
.btn-gradient-close:hover {
  background: linear-gradient(90deg, #ff4081 0%, #e040fb 100%) !important;
}
</style> 
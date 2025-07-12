# MoviePilot Vue插件开发指南

## 目录

- [1. 概述](#1-概述)
- [2. 环境准备](#2-环境准备)
- [3. 项目结构](#3-项目结构)
- [4. 插件开发流程](#4-插件开发流程)
  - [4.1 后端部分](#41-后端部分)
  - [4.2 前端部分](#42-前端部分)
- [5. 组件开发详解](#5-组件开发详解)
  - [5.1 Config组件（配置页面）](#51-config组件配置页面)
  - [5.2 Page组件（详情页面）](#52-page组件详情页面)
  - [5.3 Dashboard组件（仪表板，可选）](#53-dashboard组件仪表板可选)
- [6. API接口注册与调用](#6-api接口注册与调用)
- [7. 仪表盘实现详解](#7-仪表盘实现详解)
- [8. 打包与发布](#8-打包与发布)
- [9. 常见问题和解决方案](#9-常见问题和解决方案)
- [10. 示例代码](#10-示例代码)

## 1. 概述

MoviePilot支持通过模块联邦（Module Federation）技术实现动态插件加载。插件可以通过Vue组件实现自定义用户界面，与MoviePilot主应用集成，提供丰富的功能扩展能力。本文档详细介绍如何从零开始开发一个完整的MoviePilot Vue插件。

## 2. 环境准备

开发环境要求：

- Node.js 16+ 
- Yarn 或 npm
- Vue 3
- Vite 4+
- TypeScript（推荐）或JavaScript
- Python 3.10+（用于开发插件后端）

需要安装的关键依赖：

```bash
# 安装Vite和Vue
npm install -g vite@latest
npm install vue@latest

# 安装模块联邦插件
npm install @originjs/vite-plugin-federation --save-dev
```

## 3. 项目结构

MoviePilot插件遵循以下目录结构：

```
MoviePilot-Plugins/           # 插件仓库根目录
└── plugins/                  # 所有插件目录
    └── myplugin/             # 你的插件目录（小写）
        ├── __init__.py       # 插件主类定义文件
        ├── README.md         # 插件说明文档
        ├── requirements.txt  # 插件Python依赖
        └── src/              # 前端源代码目录
            ├── main.ts       # 前端入口文件
            ├── index.html    # 开发用HTML
            ├── vite.config.ts # Vite配置文件
            ├── package.json  # npm配置文件
            ├── components/   # Vue组件目录
            │   ├── Config.vue # 配置页面组件
            │   ├── Page.vue   # 详情页面组件
            │   └── Dashboard.vue # 仪表板组件（可选）
            └── dist/         # 构建输出目录
                └── assets/   # 资源文件（JS、CSS等）
                    └── remoteEntry.js  # 远程入口文件
```

## 4. 插件开发流程

### 4.1 后端部分

1. **创建插件目录**

首先创建插件目录，目录名应为插件ID的小写形式：

```bash
mkdir -p plugins/myplugin
cd plugins/myplugin
```

2. **编写`__init__.py`文件**

这是插件的主要Python文件，定义插件类及其行为。插件类必须继承`_PluginBase`：

```python
from typing import List, Tuple, Dict, Any, Optional
from app.plugins import _PluginBase

class MyPlugin(_PluginBase):
    # 插件信息
    plugin_name = "我的插件"
    plugin_desc = "这是一个示例插件"
    plugin_version = "1.0"
    plugin_author = "你的名字"
    author_url = "https://github.com/yourname"
    plugin_icon = "https://example.com/icon.png"  # 插件图标URL
    plugin_config_prefix = "myplugin_"  # 配置项前缀
    plugin_order = 1  # 插件加载顺序
    auth_level = 1  # 认证级别：1=所有用户，2=认证用户

    # 插件初始化
    def init_plugin(self, config: dict = None):
        if config:
            # 初始化配置
            pass
            
    # 插件前端渲染模式
    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        """返回Vue渲染模式和组件路径"""
        return "vue", "dist/assets"
    
    # 【重要】这两个方法即使在Vue模式下也必须实现
    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """
        【重要】为Vuetify模式提供配置页面的定义。
        即使使用Vue模式，这个方法也必须实现，否则将导致插件加载失败。
        Vue模式下，第一个参数返回None，第二个参数返回初始配置数据。
        """
        return None, self._get_config()
    
    def get_page(self) -> List[dict]:
        """
        【重要】为Vuetify模式提供数据页面的定义。
        即使使用Vue模式，这个方法也必须实现，否则将导致插件加载失败。
        Vue模式下，返回一个空列表即可。
        """
        return []
    
    # 注册API接口
    def get_api(self) -> List[Dict[str, Any]]:
        """注册插件API"""
        return [
            {
                "path": "/config",  # API路径为/api/v1/plugin/MyPlugin/config
                "endpoint": self._get_config,  # 处理函数
                "methods": ["GET"],  # HTTP方法
                "auth": "bear",  # 认证类型必须为bear（Vue模式必需）
                "summary": "获取配置"
            },
            {
                "path": "/status",
                "endpoint": self._get_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取状态"
            },
            {
                "path": "/dashboard_data",
                "endpoint": self._get_dashboard_data,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取仪表板数据"
            }
        ]
    
    # API处理函数示例
    def _get_config(self) -> Dict[str, Any]:
        """API处理函数：返回插件配置"""
        return {
            "setting1": self._setting1,
            "setting2": self._setting2,
        }
    
    def _get_status(self) -> Dict[str, Any]:
        """API处理函数：返回插件状态"""
        return {
            "enabled": self._enabled,
            "lastRunTime": self._last_run_time,
            "nextRunTime": self._next_run_time,
        }
    
    def _get_dashboard_data(self) -> Dict[str, Any]:
        """API处理函数：返回仪表板数据"""
        return {
            "value": 12345,
            "label": "已处理数据量"
        }
        
    # 仪表盘元信息
    def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
        """
        获取插件仪表盘元信息
        返回示例：
            [{
                "key": "dashboard1", // 仪表盘的key，在当前插件范围唯一
                "name": "仪表盘1" // 仪表盘的名称
            }, {
                "key": "dashboard2",
                "name": "仪表盘2"
            }]
        """
        return [
            {
                "key": "main_dashboard",
                "name": "插件主仪表盘"
            },
            {
                "key": "secondary_dashboard",
                "name": "插件辅助仪表盘"
            }
        ]
        
    # 仪表盘数据与配置
    def get_dashboard(self, key: str, **kwargs) -> Optional[
        Tuple[Dict[str, Any], Dict[str, Any], Optional[List[dict]]]]:
        """
        获取插件仪表盘页面，需要返回：
        1、仪表板col配置字典；
        2、全局配置（布局、自动刷新等）；
        3、仪表板页面元素配置含数据json（vuetify）或 None（vue模式）
        
        1、col配置参考：
        {
            "cols": 12, "md": 6  # 栅格宽度配置
        }
        
        2、全局配置参考：
        {
            "refresh": 10,  # 自动刷新时间，单位秒
            "border": True,  # 是否显示边框，默认True，为False时取消组件边框和边距，由插件自行控制
            "title": "组件标题",  # 组件标题，如有将显示该标题，否则显示插件名称
            "subtitle": "组件子标题",  # 组件子标题，缺省时不展示子标题
        }
        
        3、vuetify模式页面配置使用Vuetify组件拼装，参考：https://vuetifyjs.com/；
           vue模式设为None，由前端Dashboard.vue组件渲染
        
        kwargs参数可获取的值：1、user_agent：浏览器UA
        
        :param key: 仪表盘key，根据指定的key返回相应的仪表盘数据，缺省时返回一个固定的仪表盘数据（兼容旧版）
        """
        if key == "main_dashboard":
            # Vue组件模式（返回None作为第三个参数）
            return {
                "cols": 12,
                "md": 6
            }, {
                "refresh": 10,
                "border": True,
                "title": "我的仪表盘",
                "subtitle": "实时数据"
            }, None
        elif key == "secondary_dashboard":
            # Vuetify配置模式（返回配置JSON作为第三个参数）
            return {
                "cols": 12,
                "md": 6
            }, {
                "refresh": 30,
                "border": True,
                "title": "配置模式仪表盘"
            }, [
                {
                    "component": "VCard",
                    "props": {"class": "mx-auto"},
                    "content": [
                        {
                            "component": "VCardTitle",
                            "text": "数据统计"
                        },
                        {
                            "component": "VCardText",
                            "props": {"class": "d-flex justify-center text-h4"},
                            "text": "12345"
                        }
                    ]
                }
            ]
        return None
        
    def stop_service(self):
        """
        停止插件运行或清理资源。
        在MoviePilot关闭或插件卸载/禁用时调用。
        """
        # 停止所有运行中的任务
        # 清理资源
        # 例如停止定时任务：
        if hasattr(self, '_scheduler') and self._scheduler and self._scheduler.running:
            try:
                self._scheduler.shutdown(wait=False)
                # 日志记录停止成功
            except Exception as e:
                # 日志记录停止失败
                pass

3. **创建requirements.txt**

如果你的插件需要额外的Python依赖，请创建requirements.txt文件：

```
# requirements.txt
requests>=2.28.0
pydantic>=1.10.0
```

### 4.2 前端部分

1. **创建前端项目**

使用Vite创建Vue项目：

```bash
npm create vite@latest src -- --template vue-ts
cd src
npm install
```

2. **安装必要依赖**

MoviePilot前端使用Vuetify作为UI组件库，Vue模式插件**必须**使用Vuetify以保持一致的UI风格：

```bash
# 安装Vuetify（必需）
npm install vuetify@^3.0.0
```

3. **配置`vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'MyPlugin', // 必须与后端插件类名完全一致（区分大小写）
      filename: 'remoteEntry.js',
      exposes: {
        './Page': './src/components/Page.vue',
        './Config': './src/components/Config.vue',
        './Dashboard': './src/components/Dashboard.vue', // 可选
      },
      shared: {
        vue: { requiredVersion: false },
        vuetify: { requiredVersion: false },
        'vuetify/styles': { requiredVersion: false }
      },
      format: 'esm'
    })
  ],
  build: {
    target: 'esnext',   // 必须，支持顶层await
    minify: false,      // 开发时设为false便于调试
    cssCodeSplit: false,
  },
  server: {
    port: 5001,   // 与主应用不同的端口
    cors: true,   // 启用CORS
    origin: 'http://localhost:5001'
  },
})
```

4. **创建Vue组件**

在`src/components/`目录下创建三个关键组件：

## 5. 组件开发详解

### 5.1 Config组件（配置页面）

`Config.vue` - 用于配置插件参数：

```vue
<template>
  <div class="plugin-config">
    <v-card>
      <v-card-title>插件配置</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-3">{{ error }}</v-alert>
        <v-alert v-if="successMessage" type="success" density="compact" class="mb-3">{{ successMessage }}</v-alert>
        
        <v-form ref="form" v-model="isFormValid">
          <!-- 配置表单项 -->
          <v-text-field 
            v-model="editableConfig.setting1" 
            label="设置1"
            hint="设置1的说明"
            persistent-hint
          ></v-text-field>
          
          <v-switch
            v-model="editableConfig.setting2"
            label="设置2"
            color="primary"
            hint="设置2的说明"
            persistent-hint
          ></v-switch>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="info" @click="emit('switch')" prepend-icon="mdi-table">状态页</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="outlined" @click="resetConfig" prepend-icon="mdi-backup-restore">重置</v-btn>
        <v-btn color="primary" @click="saveConfig" prepend-icon="mdi-content-save">保存配置</v-btn>
        <v-btn color="grey" @click="emit('close')" prepend-icon="mdi-close">关闭</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';

// 接收props
const props = defineProps({
  initialConfig: {
    type: Object,
    default: () => ({})
  },
  api: {
    type: Object,
    required: true,
  }
});

// 定义事件
const emit = defineEmits(['close', 'switch', 'save']);

const form = ref(null);
const isFormValid = ref(true);
const error = ref(null);
const successMessage = ref(null);

// 可编辑的配置对象
const editableConfig = reactive({
  setting1: '',
  setting2: false,
});

// 初始化配置
function initConfig() {
  if (props.initialConfig) {
    Object.keys(editableConfig).forEach(key => {
      if (props.initialConfig.hasOwnProperty(key)) {
        editableConfig[key] = props.initialConfig[key];
      }
    });
  }
}

// 保存配置 - 通过emit事件
function saveConfig() {
  if (!form.value) return;
  
  try {
    // 发送保存配置请求
    emit('save', JSON.parse(JSON.stringify(editableConfig)));
    successMessage.value = '配置已保存';
    setTimeout(() => { successMessage.value = null; }, 3000);
  } catch (err) {
    error.value = '保存配置失败: ' + err.message;
    setTimeout(() => { error.value = null; }, 3000);
  }
}

// 重置配置
function resetConfig() {
  initConfig();
  successMessage.value = '配置已重置';
  setTimeout(() => { successMessage.value = null; }, 3000);
}

// 组件挂载时初始化
onMounted(() => {
  initConfig();
});
</script>

<style scoped>
.plugin-config {
  padding: 0;
}
</style>
```

### 5.2 Page组件（详情页面）

`Page.vue` - 用于显示插件状态和操作：

```vue
<template>
  <div class="plugin-page">
    <v-card>
      <v-card-title>插件状态</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-3">{{ error }}</v-alert>
        <v-alert v-if="actionMessage" :type="actionMessageType" density="compact" class="mb-3">{{ actionMessage }}</v-alert>
        
        <v-skeleton-loader v-if="loading && !dataLoaded" type="article, actions"></v-skeleton-loader>
        
        <div v-if="dataLoaded">
          <!-- 状态展示 -->
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="text-subtitle-1">当前状态</v-card-title>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title class="font-weight-bold">状态:</v-list-item-title>
                <template v-slot:append>
                  <v-chip size="small" :color="statusData.enabled ? 'success' : 'grey'">
                    {{ statusData.enabled ? '已启用' : '已禁用' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="emit('switch')" prepend-icon="mdi-cog">配置</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="info" @click="fetchStatus" :loading="loading" prepend-icon="mdi-refresh">刷新状态</v-btn>
        <v-btn color="success" @click="performAction" :loading="actionLoading" prepend-icon="mdi-flash">执行操作</v-btn>
        <v-btn color="grey" @click="emit('close')" prepend-icon="mdi-close">关闭</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';

// 接收props
const props = defineProps({
  api: {
    type: Object,
    required: true,
  }
});

// 定义事件
const emit = defineEmits(['switch', 'close']);

const loading = ref(false);
const actionLoading = ref(false);
const error = ref(null);
const actionMessage = ref(null);
const actionMessageType = ref('info');
const dataLoaded = ref(false);

// 插件ID
const pluginId = "MyPlugin";  // 必须与插件类名匹配

// 状态数据
const statusData = reactive({
  enabled: false,
  // 其他状态字段
});

// 获取状态
async function fetchStatus() {
  loading.value = true;
  error.value = null;
  actionMessage.value = null;

  try {
    // API调用，注意路径不包含/api/v1前缀
    const data = await props.api.get(`plugin/${pluginId}/status`);
    
    if (data) {
      Object.assign(statusData, data);
      dataLoaded.value = true;
    } else {
      throw new Error('获取状态响应无效或为空');
    }
  } catch (err) {
    console.error('获取状态失败:', err);
    error.value = err.message || '获取状态失败，请检查网络或API';
  } finally {
    loading.value = false;
  }
}

// 执行插件操作
async function performAction() {
  actionLoading.value = true;
  error.value = null;
  actionMessage.value = null;

  try {
    // API调用，注意路径不包含/api/v1前缀
    const data = await props.api.post(`plugin/${pluginId}/action`);
    
    if (data) {
      actionMessage.value = data.message || '操作已完成';
      actionMessageType.value = 'success';
      
      // 操作完成后刷新状态
      setTimeout(() => fetchStatus(), 1000);
    } else {
      throw new Error('操作响应无效或为空');
    }
  } catch (err) {
    console.error('执行操作失败:', err);
    error.value = err.message || '执行操作失败';
    actionMessageType.value = 'error';
  } finally {
    actionLoading.value = false;
    setTimeout(() => { actionMessage.value = null; }, 7000);
  }
}

// 组件挂载时获取状态
onMounted(() => {
  fetchStatus();
});
</script>

<style scoped>
.plugin-page {
  padding: 0;
}
</style>
```

### 5.3 Dashboard组件（仪表板，可选）

`Dashboard.vue` - 用于显示插件数据的仪表板组件：

```vue
<template>
  <div class="dashboard-widget">
    <v-card :flat="!props.config?.attrs?.border" :loading="loading" class="fill-height d-flex flex-column">
      <v-card-item v-if="props.config?.attrs?.title || props.config?.attrs?.subtitle">
        <v-card-title>{{ props.config?.attrs?.title || '插件仪表板' }}</v-card-title>
        <v-card-subtitle v-if="props.config?.attrs?.subtitle">{{ props.config.attrs.subtitle }}</v-card-subtitle>
      </v-card-item>

      <v-card-text class="flex-grow-1 pa-3">
        <!-- 加载中状态 -->
        <div v-if="loading && !initialDataLoaded" class="text-center py-2">
          <v-progress-circular indeterminate color="primary" size="small"></v-progress-circular>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="text-error text-caption d-flex align-center">
          <v-icon size="small" color="error" class="mr-1">mdi-alert-circle-outline</v-icon>
          {{ error || '数据加载失败' }}
        </div>
        
        <!-- 数据显示 -->
        <div v-else-if="initialDataLoaded && summaryData">
          <v-list density="compact" class="py-0">
            <!-- 插件状态显示 -->
            <v-list-item class="pa-0">
              <template v-slot:prepend>
                <v-icon size="small" :color="summaryData.enabled ? 'success' : 'grey'" class="mr-2">
                  {{ summaryData.enabled ? 'mdi-check-circle' : 'mdi-close-circle' }}
                </v-icon>
              </template>
              <v-list-item-title class="text-caption">
                插件状态: <span :class="summaryData.enabled ? 'text-success' : 'text-grey'">
                  {{ summaryData.enabled ? '已启用' : '已禁用' }}
                </span>
              </v-list-item-title>
            </v-list-item>

            <!-- 分隔线 -->
            <v-divider class="my-1"></v-divider>

            <!-- 数据项展示 -->
            <v-list-item class="pa-0">
              <template v-slot:prepend>
                <v-icon size="small" color="blue-grey-lighten-1" class="mr-2">mdi-counter</v-icon>
              </template>
              <v-list-item-title class="text-caption">
                数据项: {{ summaryData.dataValue || '无数据' }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </div>
        
        <!-- 空数据状态 -->
        <div v-else class="text-caption text-disabled text-center py-2">
          暂无数据
        </div>
      </v-card-text>

      <!-- 刷新按钮 -->
      <v-divider v-if="props.allowRefresh"></v-divider>
      <v-card-actions v-if="props.allowRefresh" class="px-3 py-1">
        <span class="text-caption text-disabled">{{ lastRefreshedTimeDisplay }}</span>
        <v-spacer></v-spacer>
        <v-btn icon variant="text" size="small" @click="fetchData" :loading="loading">
          <v-icon size="small">mdi-refresh</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';

// 接收props
const props = defineProps({
  // API对象，用于调用插件API
  api: { 
    type: Object,  // 注意：这里必须是Object类型，不是Function
    required: true,
  },
  // 配置参数，来自get_dashboard方法的第二个返回值
  config: {
    type: Object,
    default: () => ({ attrs: {} }),
  },
  // 是否允许手动刷新
  allowRefresh: {
    type: Boolean,
    default: false,
  },
  // 自动刷新间隔（秒）
  refreshInterval: {
    type: Number,
    default: 0, // 0表示不自动刷新
  },
});

// 状态变量
const loading = ref(false);
const error = ref(null);
const initialDataLoaded = ref(false);
const summaryData = reactive({
  enabled: null,
  dataValue: null,
  otherData: null,
});
const lastRefreshedTimestamp = ref(null);

// 刷新计时器
let refreshTimer = null;

// 插件ID获取函数 - 返回固定的插件类名
// 重要：必须与插件类名完全匹配（包括大小写）
const getPluginId = () => {
  return "MyPlugin";  // 替换为你的插件类名
};

// 获取数据的函数
async function fetchData() {
  loading.value = true;
  error.value = null;
  
  try {
    // 获取插件ID
    const pluginId = getPluginId();
    
    // 调用插件API获取数据
    // 注意：使用props.api对象（不是函数）
    const data = await props.api.get(`plugin/${pluginId}/status`);
    
    if (data) {
      // 更新数据
      summaryData.enabled = data.enabled;
      summaryData.dataValue = data.someValue;
      summaryData.otherData = data.otherData;
      
      initialDataLoaded.value = true;
      lastRefreshedTimestamp.value = Date.now();
    } else {
      throw new Error('获取数据响应无效');
    }
  } catch (err) {
    console.error('获取仪表盘数据失败:', err);
    error.value = err.message || '获取数据失败';
  } finally {
    loading.value = false;
  }
}

// 最后刷新时间显示
const lastRefreshedTimeDisplay = computed(() => {
  if (!lastRefreshedTimestamp.value) return '';
  return `上次更新: ${new Date(lastRefreshedTimestamp.value).toLocaleTimeString()}`;
});

// 组件挂载时获取数据
onMounted(() => {
  fetchData();
  
  // 设置自动刷新
  if (props.allowRefresh && props.refreshInterval > 0) {
    refreshTimer = setInterval(fetchData, props.refreshInterval * 1000);
  }
});

// 组件卸载时清除计时器
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
```

**重要提示**：
1. `api` prop 必须定义为 `Object` 类型，而不是 `Function`
2. `getPluginId` 函数必须返回与后端插件类名完全一致的字符串（包括大小写）
3. 使用 `props.api.get/post` 而不是直接使用 `fetch` 调用API

## 6. API接口注册与调用

### 注册API接口

在插件的`__init__.py`文件中，通过`get_api()`方法注册API接口：

```python
def get_api(self) -> List[Dict[str, Any]]:
    """注册插件API"""
    return [
        {
            "path": "/config",  # API路径，不需要包含/api/v1/plugin/MyPlugin
            "endpoint": self._get_config,  # 处理函数
            "methods": ["GET"],  # HTTP方法
            "auth": "bear",  # 认证类型必须为bear（Vue模式下不能使用apikey）
            "summary": "获取配置"
        },
        {
            "path": "/status",
            "endpoint": self._get_status,
            "methods": ["GET"],
            "auth": "bear",
            "summary": "获取状态"
        },
        {
            "path": "/dashboard_data",
            "endpoint": self._get_dashboard_data,
            "methods": ["GET"],
            "auth": "bear",
            "summary": "获取仪表板数据"
        }
    ]
```

### 实现API处理方法

在插件类中实现上述声明的API处理方法：

```python
def _get_config(self) -> Dict[str, Any]:
    """API处理函数：返回插件配置"""
    return {
        "setting1": self._setting1,
        "setting2": self._setting2,
    }

def _get_status(self) -> Dict[str, Any]:
    """API处理函数：返回插件状态"""
    return {
        "enabled": self._enabled,
        "lastRunTime": self._last_run_time,
        "nextRunTime": self._next_run_time,
    }
    
def _get_dashboard_data(self) -> Dict[str, Any]:
    """API处理函数：返回仪表板数据"""
    return {
        "value": 12345,
        "label": "已处理数据量"
    }
```

### 在Vue组件中调用API

在Vue组件中，通过props中提供的`api`对象调用API。这是正确的API调用方式：

```javascript
// 定义props - 注意api类型同时支持对象和函数类型
const props = defineProps({
api: { 
  type: [Object, Function],  // 同时支持对象和函数类型
  required: true,
}
});

// 获取插件ID - 必须与插件类名完全匹配
const pluginId = "MyPlugin";  // 替换为你的插件类名（区分大小写）

// 发起GET请求
async function fetchData() {
  try {
    const data = await props.api.get(`plugin/${pluginId}/status`);
    // 处理返回数据...
  } catch (error) {
    console.error('API调用失败:', error);
  }
}

// 发起POST请求，带参数
async function saveData() {
  try {
    const payload = { key: "value", enabled: true };
    const result = await props.api.post(`plugin/${pluginId}/update`, payload);
    // 处理返回结果...
  } catch (error) {
    console.error('保存数据失败:', error);
  }
}

// 当api是对象时
const data = await props.api.get(`plugin/${pluginId}/status`);

// 当api是函数时
const data = await props.api(`plugin/${pluginId}/status`, { method: 'GET' });

// POST调用示例
const result = await props.api.post(`plugin/${pluginId}/action`, payload);
// 或
const result = await props.api(`plugin/${pluginId}/action`, { 
  method: 'POST', 
  body: JSON.stringify(payload)
});
```

**常见错误及解决方法**：

1. **错误的props类型定义**：
   ```javascript
   // 错误
   api: { type: Function, required: true }
   
   // 正确
   api: { type: Object, required: true }
   ```

2. **错误的API调用方式**：
   ```javascript
   // 错误 - 将api当作函数调用
   const result = await props.api();
   // 错误 - 直接使用fetch
   const response = await fetch(`/api/v1/plugin/${pluginId}/status`);
   
   // 正确
   const data = await props.api.get(`plugin/${pluginId}/status`);
   ```

3. **错误的插件ID获取**：
   ```javascript
   // 错误 - 尝试动态获取插件ID
   const pluginId = props.api();
   
   // 正确 - 直接使用硬编码的插件类名
   const pluginId = "MyPlugin";  // 替换为你的实际插件类名
   ```

## 7. 仪表盘实现详解

仪表盘功能允许插件在MoviePilot主界面的仪表盘区域展示Widget组件，有两种实现方式：Vue组件模式和Vuetify配置模式。

### 7.1 后端实现

在插件的`__init__.py`文件中，需要实现两个关键方法：

1. **实现 `get_dashboard_meta` 方法**

此方法定义插件提供的仪表盘列表：

```python
def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
    """
    获取插件仪表盘元信息
    返回示例：
        [{
            "key": "dashboard1", // 仪表盘的key，在当前插件范围唯一
            "name": "仪表盘1" // 仪表盘的名称
        }, {
            "key": "dashboard2",
            "name": "仪表盘2"
        }]
    """
    return [
        {
            "key": "main_dashboard",
            "name": "插件主仪表盘"
        },
        {
            "key": "secondary_dashboard",
            "name": "插件辅助仪表盘"
        }
    ]
```

2. **实现 `get_dashboard` 方法**

此方法根据仪表盘key返回具体的仪表盘配置：

```python
def get_dashboard(self, key: str, **kwargs) -> Optional[
    Tuple[Dict[str, Any], Dict[str, Any], Optional[List[dict]]]]:
    """
    获取插件仪表盘页面，需要返回：
    1、仪表板col配置字典；
    2、全局配置（布局、自动刷新等）；
    3、仪表板页面元素配置含数据json（vuetify）或 None（vue模式）
    
    :param key: 仪表盘key，根据指定的key返回相应的仪表盘数据
    """
    if key == "main_dashboard":
        # Vue组件模式（返回None作为第三个参数）
        return {
            "cols": 12,  # 在超小屏幕上占据的列数
            "md": 6      # 在中等屏幕上占据的列数
        }, {
            "refresh": 10,       # 自动刷新时间（秒）
            "border": True,      # 是否显示边框
            "title": "我的仪表盘", # 仪表盘标题
            "subtitle": "实时数据"  # 仪表盘副标题
        }, None
    elif key == "secondary_dashboard":
        # Vuetify配置模式（返回配置JSON作为第三个参数）
        return {
            "cols": 12,
            "md": 6
        }, {
            "refresh": 30,
            "border": True,
            "title": "配置模式仪表盘"
        }, [
            {
                "component": "VCard",
                "props": {"class": "mx-auto"},
                "content": [
                    {
                        "component": "VCardTitle",
                        "text": "数据统计"
                    },
                    {
                        "component": "VCardText",
                        "props": {"class": "d-flex justify-center text-h4"},
                        "text": "12345"
                    }
                ]
            }
        ]
    return None
```

### 7.2 仪表盘模式选择

MoviePilot支持两种仪表盘实现模式：

1. **Vue组件模式**：由前端的Dashboard.vue组件负责渲染，适合复杂的交互
   - 在`get_dashboard`中，第三个返回参数设为`None`
   - 前端Dashboard.vue组件将被加载并渲染
   - 通过props.api调用插件API获取所需数据

2. **Vuetify配置模式**：通过JSON配置描述UI，适合简单的数据展示
   - 在`get_dashboard`中，第三个返回参数为Vuetify组件的JSON配置
   - 不需要实现前端Dashboard.vue组件
   - 数据直接包含在返回的JSON配置中

### 7.3 栅格系统配置

仪表盘使用12列栅格系统，可以通过以下设置控制组件在不同屏幕尺寸下的布局：

```python
# 栅格配置示例
{
    "cols": 12,  # 在超小屏幕（xs）上占据的列数
    "sm": 6,     # 在小屏幕（sm）上占据的列数
    "md": 4,     # 在中等屏幕（md）上占据的列数
    "lg": 3,     # 在大屏幕（lg）上占据的列数
    "xl": 2      # 在超大屏幕（xl）上占据的列数
}
```

### 7.4 全局配置参数

全局配置控制仪表盘的整体行为和外观：

```python
# 全局配置示例
{
    "refresh": 10,          # 自动刷新时间（秒）
    "border": True,         # 是否显示边框
    "title": "我的仪表盘",   # 仪表盘标题
    "subtitle": "实时数据",  # 仪表盘副标题
    "dark": False           # 是否使用暗色主题
}
```

### 7.5 Vue模式仪表盘实现要点

当你选择Vue模式实现仪表盘（`get_dashboard`方法返回`None`作为第三个参数）时，需要注意以下几点：

1. **Backend (`__init__.py`)实现**：
   ```python
   def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
       """定义仪表盘列表"""
       return [
           {
               "key": "main_dashboard",
               "name": "我的仪表盘"
           }
       ]
   
   def get_dashboard(self, key: str, **kwargs) -> Optional[
       Tuple[Dict[str, Any], Dict[str, Any], Optional[List[dict]]]]:
       """返回仪表盘配置"""
       # 第三个参数为None表示使用Vue模式
       return {
           "cols": 12,  # 栅格宽度配置
           "md": 6
       }, {
           "refresh": 30,  # 刷新时间（秒）
           "border": True,
           "title": "我的仪表盘",
           "subtitle": "仪表盘说明"
       }, None  # None表示使用Vue组件模式
   ```

2. **Frontend (`Dashboard.vue`)实现**：
   - 必须正确定义props
   - `api`必须定义为`Object`类型
   - 必须硬编码正确的插件ID来调用API
   - 数据加载必须使用`props.api.get/post`而不是直接使用fetch

3. **配置传递**：
   - `props.config.attrs`会包含`get_dashboard`方法第二个返回值的内容
   - `props.refreshInterval`是根据`refresh`值传入的（如果有）
   - `props.allowRefresh`会根据是否设置了`refresh`值决定

4. **避免重复获取数据**：
   ```javascript
   // 错误 - 多次请求相同的API
   const statusData = await props.api.get(`plugin/${pluginId}/status`);
   const otherData = await props.api.get(`plugin/${pluginId}/status`); 
   
   // 正确 - 一次请求，多处使用
   const data = await props.api.get(`plugin/${pluginId}/status`);
   const statusData = data.status;
   const otherData = data.otherInfo;
   ```

### 7.6 调试技巧

仪表盘开发中的常见问题及解决方法：

1. **仪表盘不显示**
   - 确认插件已启用
   - 检查`get_dashboard_meta`和`get_dashboard`方法是否正确实现
   - 确认方法返回值格式正确

2. **数据加载失败**
   - 在浏览器控制台查看API请求错误
   - 检查插件ID是否与后端类名完全匹配（包括大小写）
   - 核对API路径是否正确

3. **仪表盘显示但没有数据**
   - 在开发者工具的Network选项卡中检查API请求是否成功
   - 确认API返回的数据格式与组件中预期的一致
   - 添加`console.log`打印中间数据，追踪数据流向

4. **自动刷新不工作**
   - 确认`get_dashboard`方法中设置了`refresh`参数
   - 检查`onMounted`和`onUnmounted`中的定时器逻辑

## 8. 打包与发布

### 前端打包

在插件前端目录运行以下命令：

```bash
npm run build
```

这将在`dist/assets`目录下生成打包后的文件。

### 发布插件

创建或更新`package.json`，确保版本号与`__init__.py`中定义的`plugin_version`一致：

```json
{
  "name": "myplugin",
  "version": "1.0",
  "description": "这是一个示例插件",
  "author": "你的名字",
  "level": 1,
  "icon": "https://example.com/icon.png",
  "repository": {
    "type": "git",
    "url": "https://github.com/username/MoviePilot-Plugins"
  },
  "history": {
    "v1.0": "首次发布"
  }
}
```

## 9. 常见问题和解决方案

### API 404 错误

**问题**：调用插件API时返回404错误。
**解决方案**：
- 确认插件已启用。插件未启用时，API路由不会被注册
- 确认API路径正确，特别是插件ID的大小写必须与类名一致
- 检查`get_api()`方法是否正确定义了API路由

### 配置保存问题

**问题**：配置无法保存。
**解决方案**：
- 确保使用`emit('save', config)`事件来保存配置，而不是通过API调用
- 检查`editableConfig`对象结构是否与后端的配置结构匹配

### 模块联邦加载失败

**问题**：模块联邦组件加载失败。
**解决方案**：
- 检查`vite.config.ts`中的模块联邦配置
- 确保`exposes`中的组件路径正确
- 检查`shared`依赖配置
- 使用`build.target='esnext'`以支持顶层await

### 仪表盘不显示

**问题**：插件仪表盘未出现在MoviePilot仪表盘页面。
**解决方案**：
- 确认已实现`get_dashboard_meta`和`get_dashboard`方法
- 检查返回值格式是否正确
- 确认插件已启用
- 前端开发环境需要与后端同步更新到最新版本

### 样式冲突

**问题**：插件样式与主应用冲突。
**解决方案**：
- 使用`<style scoped>`确保样式只应用于组件
- 避免全局CSS选择器
- 为插件组件添加唯一前缀类名

## 10. 示例代码

完整的插件示例代码可以参考MoviePilot官方插件仓库中的示例：

- [插件示例](https://github.com/jxxghp/MoviePilot-Plugins)

## 贡献与支持

如果您发现文档中的错误或需要补充，欢迎提交PR或Issue。 
<template>
  <v-card flat class="plugin-page glass-card">
    <!-- 顶部标题栏 -->
    <v-card-title class="section-title d-flex align-center mb-1" style="padding: 10px 0 6px 0; min-height:unset;">
      <v-icon class="mr-1" color="primary" size="26">mdi-server</v-icon>
      <span style="font-size:1.15rem; font-weight:600; letter-spacing:1px;">PVE虚拟机守护神</span>
      <v-spacer />
      <v-btn
        v-if="isMobile"
        icon
        class="close-btn"
        @click="$emit('close')"
        style="margin-left:auto; background:transparent; box-shadow:none; min-width:unset; width:auto; height:auto;"
      >
        <v-icon size="28" style="color:#999;">mdi-close</v-icon>
      </v-btn>
    </v-card-title>
    <!-- 顶部状态栏：左右分栏 -->
    <v-row class="mb-4" align="stretch" dense>
      <!-- 右侧：插件状态 -->
      <v-col cols="12" md="6" class="d-flex flex-column">
        <v-card flat class="rounded border flex-grow-1 glass-card mb-4">
      <v-card-title class="text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5 section-title">
            <v-icon icon="mdi-power" :color="status.enabled ? 'success' : 'grey'" class="mr-2" />
            <span>插件状态</span>
            <v-spacer />
            <v-btn icon class="glow-btn" :loading="checking" @click="runCheckup">
              <v-icon>mdi-stethoscope</v-icon>
            </v-btn>
      </v-card-title>
      <v-card-text class="px-3 py-2">
            <div>插件状态：<v-chip :color="status.enabled ? 'success' : 'grey'" size="x-small">{{ status.enabled ? '已启用' : '已禁用' }}</v-chip></div>
            <div>CRON表达式：{{ cronDescription }}</div>
            <div>下次运行 {{ nextRunCountdown }}</div>
            <div>备份状态：<span :class="status.backup_activity === '空闲' ? 'text-success' : 'text-warning'">{{ status.backup_activity || '-' }}</span></div>
            <div>恢复状态：<span :class="status.restore_activity === '空闲' ? 'text-success' : 'text-warning'">{{ status.restore_activity || '-' }}</span></div>
      </v-card-text>
    </v-card>
      </v-col>
      <!-- 左侧：PVE主机状态  -->
      <v-col cols="12" md="6" class="d-flex flex-column">
        <v-card flat class="rounded border flex-grow-1 glass-card mb-4">
          <v-card-title class="text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5 section-title">
            <v-icon icon="mdi-server" class="mr-2" color="primary" />
            <span>PVE主机状态</span>
            <v-spacer />
            <div class="host-action-btns">
              <v-btn icon class="glow-btn" :loading="hostActionLoading === 'reboot'" @click="handleHostActionClick('reboot')">
                <v-icon size="28">mdi-restart</v-icon>
              </v-btn>
              <v-btn icon class="glow-btn" :loading="hostActionLoading === 'shutdown'" @click="handleHostActionClick('shutdown')">
                <v-icon size="28">mdi-power</v-icon>
              </v-btn>
              <v-btn icon class="glow-btn" @click="fetchPveStatus">
                <v-icon size="28">mdi-refresh</v-icon>
              </v-btn>
            </div>
          </v-card-title>
      <v-card-text class="px-3 py-2">
        <div v-if="pveStatus.online">
          <div>主机名：{{ pveStatus.hostname }}</div>
          <div>CPU：{{ pveStatus.cpu_model }} ({{ pveStatus.cpu_cores }}核) 利用率：{{ pveStatus.cpu_usage }}%</div>
          <div>内存：{{ pveStatus.mem_used }}/{{ pveStatus.mem_total }}MB ({{ pveStatus.mem_usage }}%)</div>
          <div>硬盘：{{ pveStatus.disk_used }}/{{ pveStatus.disk_total }}MB ({{ pveStatus.disk_usage }}%)</div>
          <div>负载：{{ pveStatus.load_avg?.join(' / ') }}</div>
          <div>内核：{{ pveStatus.kernel }}</div>
          <div>PVE版本：{{ pveStatus.pve_version }}</div>
        </div>
        <div v-else>
          <span style="color: red;">主机离线或连接失败：{{ pveStatus.error }}</span>
        </div>
      </v-card-text>
    </v-card>
      </v-col>
    </v-row>

    <!-- 容器状态和交互区 -->
    <v-row class="mb-4" align="stretch" dense>
      <!-- 容器状态  -->
      <v-col cols="12" class="d-flex flex-column">
        <v-card flat class="rounded border glass-card mb-4 flex-grow-1">
          <v-card-title class="text-caption d-flex align-center px-3 py-2 bg-primary-lighten-5 section-title">
        <v-icon icon="mdi-docker" class="mr-2" color="primary" />
        <span>容器状态</span>
        <v-spacer />
            <v-btn icon class="glow-btn" @click="fetchContainerStatus"><v-icon icon="mdi-refresh" /></v-btn>
      </v-card-title>
      <v-card-text class="px-3 py-2">
        <div class="mb-2 d-flex flex-wrap align-center" style="min-height: 28px;">
          <span class="mr-4">容器总数：<b>{{ containerStatus.length }}</b></span>
          <span class="mr-4">运行中：<b>{{ containerStatus.filter(c => c.status === 'running').length }}</b></span>
          <span class="mr-4">主机名：<b>{{ pveStatus.hostname || '-' }}</b></span>
          <span class="mr-4">PVE主机IP：<b>{{ pveStatus.ip || '-' }}</b></span>
        </div>
        <div v-if="!isMobile">
    <v-data-table
      :headers="containerHeaders"
      :items="containerStatus"
      class="elevation-0"
      hide-default-footer
      density="compact"
    >
      <template #item.type="{ item }">
        <v-chip size="x-small" :color="item.type === 'qemu' ? 'primary' : 'info'">{{ item.type === 'qemu' ? 'QEMU' : (item.type === 'lxc' ? 'LXC' : item.type) }}</v-chip>
      </template>
      <template #item.status="{ item }">
        <v-chip :color="item.status === 'running' ? 'success' : 'grey'" size="x-small">{{ item.status }}</v-chip>
      </template>
      <template #item.tags="{ item }">
        <span v-if="!item.tags || !item.tags.trim()">-</span>
        <template v-else>
          <v-chip
            v-for="tag in item.tags.split(/[,;]+/).map(t => t.trim()).filter(Boolean)"
            :key="tag"
            size="x-small"
            :style="{ backgroundColor: getPveTagColor(tag), color: '#fff', fontWeight: 600 }"
            class="mr-1"
          >{{ tag }}</v-chip>
        </template>
      </template>
      <template #item.uptime="{ item }">
        <span v-html="formatUptime(item.uptime)"></span>
      </template>
      <template #item.actions="{ item }">
        <div class="d-flex justify-end align-center" style="gap: 4px;">
          <v-btn size="x-small" color="success" :loading="item._actionLoading === 'start'" :disabled="item.status === 'running'" @click="handleVmAction(item, 'start')" class="mr-1">启动</v-btn>
          <v-btn size="x-small" color="error" :loading="item._actionLoading === 'stop'" :disabled="item.status !== 'running'" @click="handleVmAction(item, 'stop')" class="mr-1">关闭</v-btn>
          <v-btn size="x-small" color="info" :loading="item._actionLoading === 'reboot'" :disabled="item.status !== 'running'" @click="handleVmAction(item, 'reboot')" class="mr-1">重启</v-btn>
          <v-btn size="x-small" color="primary" :loading="item._actionLoading === 'snapshot'" @click="handleVmSnapshot(item)">创建快照</v-btn>
        </div>
      </template>
    </v-data-table>
  </div>
  <div v-else>
    <div v-for="item in containerStatus" :key="item.vmid" class="mobile-card">
      <div class="d-flex align-center mb-1">
        <span class="font-weight-bold" style="font-size:1.1em;">{{ item.displayName || item.description || item.hostname || item.name || '-' }}</span>
        <v-chip size="x-small" :color="item.type === 'qemu' ? 'primary' : 'info'" class="ml-2">{{ item.type === 'qemu' ? 'QEMU' : (item.type === 'lxc' ? 'LXC' : item.type) }}</v-chip>
        <v-chip :color="item.status === 'running' ? 'success' : 'grey'" size="x-small" class="ml-2">{{ item.status }}</v-chip>
      </div>
      <div class="d-flex align-center mb-1" style="font-size:0.95em;color:#90caf9;">
        <span>ID: {{ item.vmid }}</span>
      </div>
      <div class="d-flex align-center mb-1" style="font-size:0.95em;">
        <v-icon size="18" color="success" class="mr-1">mdi-timer-outline</v-icon>
        <span v-html="formatUptime(item.uptime)"></span>
      </div>
      <div class="mobile-actions d-flex align-center" style="gap:8px;flex-wrap:wrap;">
        <v-btn size="small" color="success" :loading="item._actionLoading === 'start'" :disabled="item.status === 'running'" @click="handleVmAction(item, 'start')">启动</v-btn>
        <v-btn size="small" color="error" :loading="item._actionLoading === 'stop'" :disabled="item.status !== 'running'" @click="handleVmAction(item, 'stop')">关闭</v-btn>
        <v-btn size="small" color="info" :loading="item._actionLoading === 'reboot'" :disabled="item.status !== 'running'" @click="handleVmAction(item, 'reboot')">重启</v-btn>
        <v-btn size="small" color="primary" :loading="item._actionLoading === 'snapshot'" @click="handleVmSnapshot(item)">快照</v-btn>
      </div>
    </div>
  </div>
</v-card-text>
      </v-card>
      </v-col>
    </v-row>

    <!-- 页面底部：任务历史和备份文件 -->

    <!-- 恢复弹窗 -->
    <v-dialog v-model="showRestoreDialog" max-width="500">
      <v-card>
        <v-card-title>选择要恢复的备份文件</v-card-title>
        <v-card-text>
          <v-select
            v-model="selectedRestoreFile"
            :items="backupFiles"
            :item-title="item => item.filename + ' (' + item.source + ')'"
            item-value="filename"
            label="备份文件"
          />
          <v-text-field v-model="restoreDisk" label="恢复存储硬盘" placeholder="请输入存储池" />
          <v-text-field v-model="restoreVmid" label="目标VMID(可选)"/>
          <v-switch v-model="restoreForce" label="强制恢复(覆盖现有VM)"/>
          <v-switch v-model="restoreSkipExisting" label="跳过已存在的VM"/>
        </v-card-text>
        <v-card-actions>
          <v-btn color="grey" @click="showRestoreDialog = false">取消</v-btn>
          <v-btn color="success" :loading="loadingRestore" @click="runRestore" :disabled="!selectedRestoreFile">确认恢复</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 进度条/提示 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout">
      {{ snackbar.text }}
    </v-snackbar>

    <!-- 删除确认弹窗 -->
    <v-dialog v-model="showDeleteDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">删除确认</v-card-title>
        <v-card-text>
          <div class="mb-2">
            确定要删除备份文件
            <span class="font-weight-bold" style="color:#d32f2f">{{ deleteTarget?.filename }}</span>
            吗？
          </div>
          <div v-if="deleteTarget">
            <v-chip size="small" color="primary" class="mr-2">{{ deleteTarget.source }}</v-chip>
            <span class="grey--text text--darken-1">{{ deleteTarget.size_mb ? (deleteTarget.size_mb.toFixed(2) + ' MB') : '-' }}</span>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="grey" @click="showDeleteDialog = false" :disabled="deleteLoading">取消</v-btn>
          <v-btn color="error" :loading="deleteLoading === (deleteTarget?.filename + deleteTarget?.source)" @click="handleDeleteConfirm">
            删除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 底部固定操作栏 -->
    <v-card-actions class="px-2 py-1 footer-btns">
      <v-btn class="glow-btn glow-btn-blue" size="small" prepend-icon="mdi-history" @click="showHistoryDialog = true">任务历史</v-btn>
      <v-btn class="glow-btn glow-btn-cyan" size="small" prepend-icon="mdi-file-document-multiple" @click="openBackupFilesDialog">备份文件</v-btn>
      <v-btn class="glow-btn glow-btn-purple" size="small" prepend-icon="mdi-cube-outline" @click="openTemplateImagesDialog" :disabled="!cleanupTemplateImagesEnabled">镜像模板</v-btn>
      <v-spacer />
      <v-btn class="glow-btn glow-btn-gold" size="small" prepend-icon="mdi-broom" :disabled="!status.enabled || !status.enable_log_cleanup" :loading="loadingCleanupLogs" @click="handleCleanupLogs">清理系统日志</v-btn>
      <v-btn class="glow-btn glow-btn-orange" size="small" prepend-icon="mdi-broom" :loading="loadingClear" @click="clearHistory">清理历史记录</v-btn>
      <v-spacer />
      <v-btn class="glow-btn glow-btn-purple" size="small" prepend-icon="mdi-restore" :loading="loadingRestore" :disabled="!status.enabled || !status.enable_restore" @click="openRestoreDialog()">立即恢复</v-btn>
      <v-btn class="glow-btn glow-btn-green" size="small" prepend-icon="mdi-database-arrow-up" :loading="loadingBackup" :disabled="!status.enabled" @click="runBackup">立即备份</v-btn>
      <v-spacer />
      <v-btn class="glow-btn glow-btn-pink" size="small" prepend-icon="mdi-cog" @click="$emit('switch')">配置</v-btn>
    </v-card-actions>

    <!-- 历史记录弹窗 -->
    <v-dialog v-model="showHistoryDialog" max-width="900">
      <v-card>
        <v-card-title class="text-h6">任务历史</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="[
              { text: '时间', value: 'timestamp' },
              { text: '类型', value: 'type' },
              { text: '状态', value: 'success' },
              { text: '详情', value: 'message' },
              { text: '消息', value: 'details' }
            ]"
            :items="history"
            class="elevation-0"
            hide-default-footer
            density="compact"
            style="max-height: 500px; overflow-y: auto;"
          >
            <template #item.timestamp="{ item }">
              {{ formatTime(item.timestamp) }}
            </template>
            <template #item.success="{ item }">
              <v-chip :color="item.success ? 'success' : 'error'" size="small">
                {{ item.success ? '成功' : '失败' }}
              </v-chip>
            </template>
            <template #item.type="{ item }">
              <v-chip :color="item.type === '备份' ? 'primary' : 'purple'" size="small">{{ item.type }}</v-chip>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="showHistoryDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 备份文件弹窗 -->
    <v-dialog v-model="showBackupFilesDialog" max-width="1400">
      <v-card>
        <v-card-title class="text-h6" style="padding:8px 16px 0 16px;font-size:18px;">备份文件</v-card-title>
        <v-card-text style="padding:0 16px 8px 16px;">
          <v-data-table
            :headers="backupFileHeaders"
            :items="backupFiles"
            item-key="filenameWithSource"
            class="elevation-0"
            hide-default-footer
            density="compact"
            style="margin:0;padding:0;"
          >
            <template #item.filename="{ item }">
              {{ item.filename }}
            </template>
            <template #item.size_mb="{ item }">
              {{ item.size_mb ? item.size_mb.toFixed(2) : '-' }}
            </template>
            <template #item.date="{ item }">
              {{ item.time_str ? item.time_str.split(' ')[0] : '-' }}
            </template>
            <template #item.time="{ item }">
              {{ item.time_str ? (item.time_str.split(' ')[1] || '-') : '-' }}
            </template>
            <template #item.actions="{ item }">
              <div class="d-flex align-center" style="gap: 4px;">
                <v-tooltip v-if="!status.enabled" text="请先启用插件">
                  <template #activator="{ props }">
                    <v-btn icon size="x-small" :disabled="!status.enabled" v-bind="props"><v-icon icon="mdi-download" /></v-btn>
                  </template>
                </v-tooltip>
                <v-btn v-else icon size="x-small" @click="downloadBackup(item)"><v-icon icon="mdi-download" /></v-btn>
                <v-tooltip v-if="!status.enabled || !status.enable_restore" text="请先启用插件并开启恢复功能">
                  <template #activator="{ props }">
                    <v-btn icon size="x-small" color="success" :disabled="!status.enabled || !status.enable_restore" v-bind="props"><v-icon icon="mdi-restore" /></v-btn>
                  </template>
                </v-tooltip>
                <v-btn v-else icon size="x-small" color="success" @click="openRestoreDialog(item)"><v-icon icon="mdi-restore" /></v-btn>
                <v-tooltip v-if="!status.enabled" text="请先启用插件">
                  <template #activator="{ props }">
                    <v-btn icon size="x-small" color="error" :disabled="!status.enabled" v-bind="props"><v-icon icon="mdi-delete" /></v-btn>
                  </template>
                </v-tooltip>
                <v-btn v-else icon size="x-small" color="error" @click="confirmDelete(item)"><v-icon icon="mdi-delete" /></v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="showBackupFilesDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 体检报告弹窗 -->
    <v-dialog v-model="showCheckupDialog" max-width="480">
      <v-card>
        <v-card-title class="d-flex align-center">
          <span style="font-size:1.6rem; margin-right:8px;">{{ checkupReport.avatar }}</span>
          <span style="font-size:1.15rem; font-weight:600;">体检报告</span>
          <v-spacer/>
          <v-btn icon @click="showCheckupDialog=false"><v-icon>mdi-close</v-icon></v-btn>
        </v-card-title>
        <v-card-text>
          <div style="font-size:1.1rem; font-weight:600; color:#00eaff; margin-bottom:8px;">总分：{{ checkupReport.total || 0 }}/100</div>
          <div style="margin-bottom:8px; color:#2196f3;">{{ checkupReport.comment }}</div>
          <v-list dense>
            <v-list-item v-for="item in checkupReport.items" :key="item.label">
              <v-list-item-content>
                <v-list-item-title>{{ item.label }}：<b>{{ item.result }}</b> <span style="color:#00eaff;">+{{ item.score }}</span></v-list-item-title>
                <v-list-item-subtitle style="font-size:0.95rem; color:#90caf9;">{{ item.detail }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
          <div style="margin-top:12px; color:#ffb300; font-size:1.05rem;">{{ checkupReport.blessing }}</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn color="primary" @click="showCheckupDialog=false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>

  <!-- 主机操作确认弹窗 -->
  <v-dialog v-model="showHostActionDialog" max-width="400">
    <v-card>
      <v-card-title class="d-flex align-center" :style="`color:${pendingHostAction==='shutdown'?'#d32f2f':'#1976d2'};font-weight:600;`">
        <v-icon :color="pendingHostAction==='shutdown'?'error':'info'" size="32" class="mr-2">
          {{ pendingHostAction==='shutdown' ? 'mdi-power' : 'mdi-restart' }}
        </v-icon>
        {{ pendingHostAction==='shutdown' ? '关机主机' : '重启主机' }}
      </v-card-title>
      <v-card-text>
        <div style="font-size:1.1em;">
          确定要<strong>{{ pendingHostAction==='shutdown' ? '关机' : '重启' }}</strong>当前PVE主机吗？<br/>
          <span v-if="pendingHostAction==='shutdown'" style="color:#d32f2f;">关机后需物理开机或远程唤醒！</span>
          <span v-else style="color:#1976d2;">重启期间主机将短暂不可用。</span>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text color="grey" @click="showHostActionDialog=false" :disabled="hostActionLoading === pendingHostAction">取消</v-btn>
        <v-btn :color="pendingHostAction==='shutdown'?'error':'info'" :loading="hostActionLoading === pendingHostAction" @click="doHostAction">
          确认{{ pendingHostAction==='shutdown' ? '关机' : '重启' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- 镜像模板管理弹窗 -->
  <v-dialog v-model="showTemplateImagesDialog" max-width="1400">
    <v-card>
      <v-card-title class="text-h6" style="padding:8px 16px 0 16px;font-size:18px;">镜像模板管理</v-card-title>
      <v-card-text style="padding:0 16px 8px 16px;">
        <v-data-table
          :headers="templateImageHeaders.filter(h => h.value !== 'actions')"
          :items="templateImages"
          item-key="filenameWithType"
          class="elevation-0"
          hide-default-footer
          density="compact"
          style="margin:0;padding:0;"
        >
          <template #item.filename="{ item }">
            {{ item.filename }}
          </template>
          <template #item.type="{ item }">
            <v-chip size="x-small" :color="item.type === 'iso' ? 'info' : 'purple'">{{ item.type === 'iso' ? 'ISO镜像' : 'CT模板' }}</v-chip>
          </template>
          <template #item.size_mb="{ item }">
            {{ item.size_mb ? item.size_mb.toFixed(2) : '-' }}
          </template>
          <template #item.date="{ item }">
            {{ item.date || '-' }}
          </template>
        </v-data-table>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" class="ml-2" @click="showTemplateImagesDialog = false">关闭</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import cronstrue from 'cronstrue';
import 'cronstrue/locales/zh_CN';
dayjs.extend(duration);
// PVE标签色数组（可根据实际PVE配色调整）
const pveTagColors = [
  '#e573b7', // 粉
  '#bdb76b', // 黄褐
  '#81c784', // 绿
  '#ba68c8', // 紫
  '#ffd54f', // 黄
  '#64b5f6', // 蓝
  '#4db6ac', // 青
  '#f06292', // 粉2
  '#9575cd', // 紫2
  '#90caf9'  // 浅蓝
];
function getPveTagColor(tag) {
  // 简单hash算法，将标签内容hash到颜色数组
  let hash = 0;
  for (let i = 0; i < tag.length; i++) {
    hash = ((hash << 5) - hash) + tag.charCodeAt(i);
    hash |= 0;
  }
  const idx = Math.abs(hash) % pveTagColors.length;
  return pveTagColors[idx];
}
const props = defineProps({ api: { type: [Object, Function], required: true } });
const emit = defineEmits(['switch', 'close']);

const status = ref({});
const backupFiles = ref([]);
const history = ref([]);
const loadingBackup = ref(false);
const loadingRestore = ref(false);
const loadingClear = ref(false);
const showRestoreDialog = ref(false);
const selectedRestoreFile = ref(null);
const restoreVmid = ref('');
const restoreForce = ref(false);
const restoreSkipExisting = ref(true);
const restoreDisk = ref('');
const storageOptions = ref([]);
const loadingStorages = ref(false);
const snackbar = ref({ show: false, text: '', color: 'success', timeout: 3000 });
const deleteLoading = ref(null);
const showDeleteDialog = ref(false);
const deleteTarget = ref(null);
const showHistoryDialog = ref(false);
const pveStatus = ref({});
const loadingPveStatus = ref(true);
const containerStatus = ref([]);
const loadingContainerStatus = ref(true);
const containerHeaders = [
  { text: 'ID', value: 'vmid' },
  { text: '名称', value: 'displayName' },
  { text: '类型', value: 'type' },
  { text: '状态', value: 'status' },
  { text: '标签', value: 'tags' },
  { text: '运行时间', value: 'uptime' },
  { text: '操作', value: 'actions', sortable: false },
];
const showBackupFilesDialog = ref(false);
const selectedBackupFiles = ref([]);
const checkedBackupFiles = ref([]); // 手动多选 key 列表
const allChecked = computed({
  get() {
    return backupFiles.value.length > 0 && checkedBackupFiles.value.length === backupFiles.value.length;
  },
  set(val) {
    if (val) {
      checkedBackupFiles.value = backupFiles.value.map(f => f.filenameWithSource);
    } else {
      checkedBackupFiles.value = [];
    }
  }
});
function toggleAll() {
  if (checkedBackupFiles.value.length === backupFiles.value.length) {
    checkedBackupFiles.value = [];
  } else {
    checkedBackupFiles.value = backupFiles.value.map(f => f.filenameWithSource);
  }
}
const backupFileHeaders = [
  { text: '文件名', value: 'filename' },
  { text: '类型', value: 'source' },
  { text: '大小(MB)', value: 'size_mb' },
  { text: '日期', value: 'date' },
  { text: '时间', value: 'time' },
  { text: '备份路径', value: 'path' },
  { text: '操作', value: 'actions', sortable: false }
];

function showTip(text, color = 'success') {
  snackbar.value.text = text;
  snackbar.value.color = color;
  snackbar.value.show = true;
}

function formatTime(ts) {
  if (!ts) return '-';
  const d = new Date(ts * 1000);
  return d.toLocaleString();
}

function scrollToHistory() {
  showHistoryDialog.value = true;
}

async function fetchStatus() {
  try {
    status.value = await props.api.get('plugin/ProxmoxVEBackup/status');
    // 新增：同步镜像模板开关
    if (status.value && typeof status.value.cleanup_template_images !== 'undefined') {
      cleanupTemplateImagesEnabled.value = !!status.value.cleanup_template_images;
    } else {
      // 兼容老后端
      cleanupTemplateImagesEnabled.value = false;
    }
  } catch (e) {
    showTip('获取状态失败: ' + (e?.message || '未知错误'), 'error');
    cleanupTemplateImagesEnabled.value = false;
  }
}

async function fetchHistory() {
  try {
    const [backup, restore] = await Promise.all([
      props.api.get('plugin/ProxmoxVEBackup/backup_history'),
      props.api.get('plugin/ProxmoxVEBackup/restore_history')
    ]);
    // 合并并加类型
    const backupList = Array.isArray(backup) ? backup.map(item => ({ ...item, type: '备份' })) : [];
    const restoreList = Array.isArray(restore) ? restore.map(item => ({ ...item, type: '恢复' })) : [];
    // 合并并按时间倒序
    history.value = [...backupList, ...restoreList].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
  } catch (e) {
    showTip('获取历史记录失败: ' + (e?.message || '未知错误'), 'error');
  }
}

// 1. fetchPveStatus 成功后写入 localStorage
async function fetchPveStatus() {
  loadingPveStatus.value = true;
  try {
    const data = await props.api.get('plugin/ProxmoxVEBackup/pve_status');
    pveStatus.value = data;
    localStorage.setItem('pveStatus', JSON.stringify(data));
  } catch (e) {
    pveStatus.value = { online: false, error: e?.message || '获取失败' };
  }
  loadingPveStatus.value = false;
}
// 2. fetchContainerStatus 成功后写入 localStorage
async function fetchContainerStatus() {
  loadingContainerStatus.value = true;
  try {
    const data = await props.api.get('plugin/ProxmoxVEBackup/container_status');
    containerStatus.value = data;
    localStorage.setItem('containerStatus', JSON.stringify(data));
  } catch (e) {
    containerStatus.value = [{ error: e?.message || '获取失败' }];
  }
  loadingContainerStatus.value = false;
}

async function fetchStorages() {
  loadingStorages.value = true;
  try {
    const res = await axios.get('/api/v1/plugin/ProxmoxVEBackup/storages');
    if (res.data && res.data.success && Array.isArray(res.data.storages)) {
      storageOptions.value = res.data.storages.map(s => ({
        label: `${s.name}（${s.type}，可用${s.avail}/总${s.total}）`,
        value: s.name
      }));
      // 默认选第一个
      if (!restoreDisk.value && storageOptions.value.length > 0) {
        restoreDisk.value = storageOptions.value[0].value;
      }
    } else {
      storageOptions.value = [];
    }
  } catch (e) {
    storageOptions.value = [];
  }
  loadingStorages.value = false;
}

async function runBackup() {
  loadingBackup.value = true;
  try {
    const res = await props.api.post('plugin/ProxmoxVEBackup/run_backup');
    if (res.success) {
      showTip(res.message || '备份任务已启动');
    await fetchStatus();
    await fetchHistory();
    } else {
      showTip(res.message || '备份失败', 'error');
    }
  } catch (e) {
    showTip('备份失败: ' + (e?.message || '未知错误'), 'error');
  }
  loadingBackup.value = false;
}

function openRestoreDialog(file) {
  if (file && file.filename && file.source) selectedRestoreFile.value = file.filename;
  else selectedRestoreFile.value = null;
  if (!restoreDisk.value) restoreDisk.value = 'local';
  fetchStorages(); // 打开弹窗时加载存储池
  showRestoreDialog.value = true;
}

async function runRestore() {
  const fileObj = backupFiles.value.find(f => f.filename === selectedRestoreFile.value);
  if (!fileObj || !fileObj.filename || !fileObj.source) {
    return showTip('请选择备份文件', 'error');
  }
  loadingRestore.value = true;
  try {
    const res = await props.api.post('plugin/ProxmoxVEBackup/restore', {
      filename: fileObj.filename,
      source: fileObj.source,
      restore_vmid: restoreVmid.value,
      restore_force: restoreForce.value,
      restore_skip_existing: restoreSkipExisting.value,
      restore_storage: restoreDisk.value
    });
    if (res.success) {
      showTip(res.message || '恢复任务已启动');
      await fetchStatus();
      await fetchHistory();
    } else {
      showTip(res.message || '恢复失败', 'error');
    }
  } catch (e) {
    showTip('恢复失败: ' + (e?.message || '未知错误'), 'error');
  }
  loadingRestore.value = false;
  showRestoreDialog.value = false;
}

async function clearHistory() {
  loadingClear.value = true;
  try {
    await props.api.post('plugin/ProxmoxVEBackup/clear_history');
    showTip('历史已清理');
    await fetchHistory();
  } catch (e) {
    showTip('清理失败: ' + (e?.message || '未知错误'), 'error');
  }
  loadingClear.value = false;
}

function openBackupFilesDialog() {
  fetchBackupFiles();
  showBackupFilesDialog.value = true;
  checkedBackupFiles.value = [];
}

async function fetchBackupFiles() {
  try {
    // 直接请求 available_backups 接口，获取备份文件列表
    const files = await props.api.get('plugin/ProxmoxVEBackup/available_backups');
    if (Array.isArray(files)) {
      backupFiles.value = files.map(f => ({
        ...f,
        filenameWithSource: f.filename + '_' + f.source
      }));
    } else {
      backupFiles.value = [];
    }
  } catch (e) {
    backupFiles.value = [];
  }
}

async function downloadBackup(item) {
  // 获取 apikey（假设登录后已存到 localStorage 或 window 变量）
  const apikey = window.API_TOKEN || localStorage.getItem('api_token') || '';
  const params = new URLSearchParams({ filename: item.filename, source: item.source });
  if (apikey) params.append('apikey', apikey); // 新增 apikey
  const url = '/api/v1/plugin/ProxmoxVEBackup/download_backup?' + params.toString();
  try {
    const res = await axios.get(
      url,
      { responseType: 'blob' }
    );
    // 处理文件名
    let filename = item.filename || 'backup.dat';
    const disposition = res.headers['content-disposition'];
    if (disposition) {
      const match = disposition.match(/filename="?([^";]+)"?/);
      if (match) filename = decodeURIComponent(match[1]);
    }
    // 创建blob下载
    const blobUrl = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  } catch (error) {
    alert('下载失败: ' + (error.message || '未知错误'));
  }
}

function confirmDelete(item) {
  deleteTarget.value = item;
  showDeleteDialog.value = true;
}

async function handleDeleteConfirm() {
  if (!deleteTarget.value) return;
  deleteLoading.value = deleteTarget.value.filename + deleteTarget.value.source;
  try {
    await props.api.post('plugin/ProxmoxVEBackup/delete_backup', {
      filename: deleteTarget.value.filename,
      source: deleteTarget.value.source
    });
    showTip('删除成功');
    await fetchBackupFiles();
  } catch (e) {
    showTip('删除失败: ' + (e?.message || '未知错误'), 'error');
  }
  deleteLoading.value = null;
  showDeleteDialog.value = false;
}

function getSelectedBackupFiles() {
  return backupFiles.value.filter(f => checkedBackupFiles.value.includes(f.filenameWithSource));
}

async function batchDownload() {
  for (const item of getSelectedBackupFiles()) {
    try {
      await downloadBackup(item);
    } catch (e) {
      // console.error('批量下载单个文件失败:', e);
    }
    await new Promise(r => setTimeout(r, 500)); // 每次间隔500ms，避免并发
  }
}

async function batchRestore() {
  for (const item of getSelectedBackupFiles()) {
    openRestoreDialog(item);
  }
}

async function batchDelete() {
  for (const item of getSelectedBackupFiles()) {
    await props.api.post('plugin/ProxmoxVEBackup/delete_backup', {
      filename: item.filename,
      source: item.source
    });
  }
  showTip('批量删除完成');
  await fetchBackupFiles();
}

// 体检相关
const checking = ref(false);
const showCheckupDialog = ref(false);
const checkupReport = ref({});
const checkupBlessings = [
  '守护神为你点赞！',
  '一切正常，继续加油！',
  '健康无忧，数据安全！',
  '今日运势：大吉！',
  '守护神祝你好运连连~',
  '干得漂亮，继续保持！',
  '发现小问题，别担心，守护神帮你盯着！',
];
const checkupAvatars = [
  '😃', '😎', '🤖', '🦾', '🛡️', '✨', '🥳'
];
function runCheckup() {
  checking.value = true;
  // 模拟体检流程，实际可用API/现有数据
  setTimeout(() => {
    // 检查项
    const items = [];
    // 主机在线
    items.push({
      label: '主机连通性',
      result: pveStatus.value.online ? '正常' : '异常',
      score: pveStatus.value.online ? 20 : 0,
      detail: pveStatus.value.online ? '主机在线' : '主机离线或连接失败'
    });
    // 插件配置
    const configOk = status.value && status.value.enabled && status.value.cron;
    items.push({
      label: '插件配置',
      result: configOk ? '完整' : '不完整',
      score: configOk ? 20 : 5,
      detail: configOk ? '配置项齐全' : '部分配置缺失或未启用'
    });
    // 备份空间
    let diskScore = 15;
    let diskDetail = '-';
    if (pveStatus.value.disk_total && pveStatus.value.disk_used) {
      const used = Number(pveStatus.value.disk_used);
      const total = Number(pveStatus.value.disk_total);
      const percent = total ? (used / total) * 100 : 0;
      if (percent < 80) {
        diskScore = 20;
        diskDetail = `空间充足 (${used}/${total}MB)`;
      } else if (percent < 95) {
        diskScore = 10;
        diskDetail = `空间偏紧 (${used}/${total}MB)`;
      } else {
        diskScore = 2;
        diskDetail = `空间严重不足 (${used}/${total}MB)`;
      }
    }
    items.push({
      label: '备份空间',
      result: diskScore >= 15 ? '充足' : (diskScore >= 10 ? '偏紧' : '不足'),
      score: diskScore,
      detail: diskDetail
    });
    // 最近备份
    let backupScore = 15;
    let backupDetail = '-';
    if (history.value && history.value.length > 0) {
      const last = history.value.find(h => h.type === '备份');
      if (last && last.success) {
        backupScore = 20;
        backupDetail = '最近备份成功';
      } else {
        backupScore = 5;
        backupDetail = '最近备份失败或无记录';
      }
    }
    items.push({
      label: '最近备份',
      result: backupScore >= 20 ? '成功' : '异常',
      score: backupScore,
      detail: backupDetail
    });
    // 容器运行
    let runningNum = 0;
    if (containerStatus.value && Array.isArray(containerStatus.value)) {
      runningNum = containerStatus.value.filter(c => c.status === 'running').length;
    }
    items.push({
      label: '容器运行',
      result: runningNum > 0 ? '正常' : '全部停止',
      score: runningNum > 0 ? 15 : 5,
      detail: `运行中：${runningNum} 个`
    });
    // 总分
    const total = items.reduce((sum, i) => sum + i.score, 0);
    // 守护神表情和祝福
    const avatar = checkupAvatars[Math.floor(Math.random() * checkupAvatars.length)];
    const blessing = checkupBlessings[Math.floor(Math.random() * checkupBlessings.length)];
    checkupReport.value = {
      items,
      total,
      avatar,
      blessing,
      comment: total >= 85 ? '一切健康，守护神很满意！' : (total >= 60 ? '有小问题，建议关注！' : '健康欠佳，请尽快处理！')
    };
    checking.value = false;
    showCheckupDialog.value = true;
    // 体检完成能量+5（如有守护神能量系统可加）
    // 可在此处emit事件或调用能量加分逻辑
  }, 1200);
}

// 计算"还有多久"
const nextRunCountdown = computed(() => {
  if (!status.value.next_run_time) return '-';
  const now = dayjs();
  const next = dayjs(status.value.next_run_time);
  if (!next.isValid() || next.isBefore(now)) return '-';
  const diff = next.diff(now);
  const d = dayjs.duration(diff);
  let years = Math.floor(d.asYears());
  let days = d.days();
  let hours = d.hours();
  let minutes = d.minutes();
  let parts = [];
  if (years > 0) parts.push(`${years}年`);
  if (days > 0) parts.push(`${days}天`);
  if (hours > 0) parts.push(`${hours}小时`);
  if (minutes > 0) parts.push(`${minutes}分`);
  if (parts.length === 0) parts.push('不到1分钟');
  return parts.join('');
});

// 计算 CRON 表达式描述
const cronDescription = computed(() => {
  if (!status.value.cron) return '未配置';
  try {
    return cronstrue.toString(status.value.cron, { locale: 'zh_CN' });
  } catch (e) {
    return '解析失败';
  }
});

// 3. onMounted 时先从 localStorage 读取缓存
onMounted(async () => {
  // 自动获取API_TOKEN
  try {
    const res = await props.api.get('plugin/ProxmoxVEBackup/token');
    if (res && res.api_token) {
      window.API_TOKEN = res.api_token;
      localStorage.setItem('api_token', res.api_token);
    }
  } catch (e) {
    // console.warn('获取API令牌失败', e);
  }
  // 先读缓存
  try {
    const cachePve = localStorage.getItem('pveStatus');
    if (cachePve) pveStatus.value = JSON.parse(cachePve);
  } catch {}
  try {
    const cacheContainer = localStorage.getItem('containerStatus');
    if (cacheContainer) containerStatus.value = JSON.parse(cacheContainer);
  } catch {}
  // 再异步刷新
  fetchStatus();
  fetchHistory();
  fetchPveStatus();
  setInterval(fetchStatus, 10000);
  setInterval(fetchPveStatus, 15000);
  fetchContainerStatus();
  setInterval(fetchContainerStatus, 30000);
  fetchBackupFiles();
});

const actionLoadingMap = ref({});
async function handleVmAction(item, action) {
  const key = item.vmid + '_' + item.type;
  actionLoadingMap.value[key] = action;
  item._actionLoading = action;
  try {
    const res = await props.api.post('plugin/ProxmoxVEBackup/container_action', {
      vmid: item.vmid,
      type: item.type,
      action
    });
    showTip(res.message || (action + '操作完成'), res.success ? 'success' : 'error');
    await fetchContainerStatus();
  } catch (e) {
    showTip('操作失败: ' + (e?.message || '未知错误'), 'error');
  }
  actionLoadingMap.value[key] = null;
  item._actionLoading = null;
}

async function handleVmSnapshot(item) {
  const key = item.vmid + '_' + item.type;
  item._actionLoading = 'snapshot';
  try {
    const res = await props.api.post('plugin/ProxmoxVEBackup/container_snapshot', {
      vmid: item.vmid,
      type: item.type
    });
    showTip(res.message || '快照操作完成', res.success ? 'success' : 'error');
    await fetchContainerStatus();
  } catch (e) {
    showTip('快照失败: ' + (e?.message || '未知错误'), 'error');
  }
  item._actionLoading = null;
}

function formatUptime(uptime) {
  const sec = Number(uptime);
  if (!sec || isNaN(sec) || sec <= 0) return '<span style="color:#888;">未运行</span>';
  if (sec < 60) return '<span style="color:#4caf50;font-weight:600;">刚启动</span>';
  const days = Math.floor(sec / 86400);
  const hours = Math.floor((sec % 86400) / 3600);
  const mins = Math.floor((sec % 3600) / 60);
  let parts = [];
  if (days > 0) parts.push(days + '天');
  if (hours > 0) parts.push(hours + '小时');
  if (mins > 0) parts.push(mins + '分');
  return `<span style="color:#4caf50;font-weight:600;">运行${parts.join('')}</span>`;
}

const isMobile = ref(false);
onMounted(() => {
  const check = () => isMobile.value = window.innerWidth < 600;
  check();
  window.addEventListener('resize', check);
});

const showHostActionDialog = ref(false);
const pendingHostAction = ref(''); // reboot/shutdown
const hostActionLoading = ref('');
const handleHostActionClick = (action) => {
  if (hostActionLoading.value) return;
  pendingHostAction.value = action;
  showHostActionDialog.value = true;
};
const doHostAction = async () => {
  const action = pendingHostAction.value;
  if (!action) return;
  hostActionLoading.value = action;
  try {
    const actionText = action === 'reboot' ? '重启' : '关机';
    const res = await props.api.post('plugin/ProxmoxVEBackup/host_action', { action });
    if (res.success) {
      showTip(res.msg || `${actionText}命令已发送`);
      setTimeout(fetchPveStatus, 2000);
    } else {
      showTip(res.msg || `${actionText}失败`);
    }
  } catch (e) {
    showTip(e.message || '操作失败');
  }
  hostActionLoading.value = '';
  showHostActionDialog.value = false;
  pendingHostAction.value = '';
};

const loadingCleanupLogs = ref(false);
async function handleCleanupLogs() {
  if (!status.value.enabled || !status.value.enable_log_cleanup) return;
  loadingCleanupLogs.value = true;
  try {
    const res = await props.api.post('plugin/ProxmoxVEBackup/cleanup_logs');
    let detail = '';
    if (res.result && typeof res.result === 'object') {
      detail = Object.entries(res.result).map(([k, v]) => {
        const [count, err] = v;
        if (err) return `${k}：失败（${err}）`;
        if (count === null || typeof count === 'undefined') return `${k}：已清理`;
        return `${k}：已清理${count}个`;
      }).join('\n');
    }
    showTip((res.msg || '系统日志清理完成') + (detail ? '\n' + detail : ''), res.success ? 'success' : 'error');
  } catch (e) {
    showTip(e?.msg || e?.message || '系统日志清理失败', 'error');
  }
  loadingCleanupLogs.value = false;
}

const cleanupTemplateImagesEnabled = ref(false); // 镜像模板开关联动
const showTemplateImagesDialog = ref(false);
const templateImages = ref([]);
const templateImageHeaders = [
  { text: '文件名', value: 'filename' },
  { text: '类型', value: 'type' },
  { text: '大小(MB)', value: 'size_mb' },
  { text: '日期', value: 'date' }
  // 不再有操作列
];
function openTemplateImagesDialog() {
  fetchTemplateImages();
  showTemplateImagesDialog.value = true;
}
async function fetchTemplateImages() {
  try {
    const files = await props.api.get('plugin/ProxmoxVEBackup/template_images');
    if (Array.isArray(files)) {
      templateImages.value = files.map(f => ({
        ...f,
        filenameWithType: f.filename + '_' + f.type
      }));
    } else {
      templateImages.value = [];
    }
  } catch (e) {
    templateImages.value = [];
  }
}
</script>

<style scoped>
.plugin-page { max-width: 80rem; margin: 0 auto; padding: 0.5rem; }

/* 玻璃拟态卡片样式 */
.glass-card {
  background: rgba(40, 50, 70, 0.75);
  border-radius: 18px;
  box-shadow: 0 4px 32px 0 #00eaff22, 0 1.5px 8px 0 #0006;
  backdrop-filter: blur(8px);
  border: 1.5px solid #00eaff33;
  margin-bottom: 32px;
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
.glow-btn {
  border-radius: 10px;
  font-weight: 500;
  min-width: 90px;
  background: linear-gradient(90deg, #00eaff 0%, #3f51b5 100%);
  color: #fff !important;
  box-shadow: 0 2px 16px 0 #00eaff55;
  transition: box-shadow 0.3s, background 0.3s;
}
.glow-btn:hover {
  box-shadow: 0 4px 32px 0 #00eaffcc;
  background: linear-gradient(90deg, #3f51b5 0%, #00eaff 100%);
}
.tight-switch {
  margin-bottom: -8px;
  margin-top: -8px;
}
.section-title .v-icon {
  filter: drop-shadow(0 0 8px #00eaff88);
}
.footer-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}
.glow-icon-btn {
  border-radius: 50%;
  box-shadow: 0 0 8px #00eaff55, 0 2px 8px #0003;
  background: linear-gradient(135deg, #232a3a 60%, #00eaff22 100%);
  transition: box-shadow 0.2s, background 0.2s;
}
.glow-icon-btn:hover {
  box-shadow: 0 0 16px #00eaffcc, 0 4px 16px #0005;
  background: linear-gradient(135deg, #00eaff44 0%, #232a3a 100%);
}
.host-action-btns {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
}
@media (max-width: 600px) {
  .footer-btns {
    flex-direction: column;
    align-items: stretch;
  }
  .mobile-card {
    margin-bottom: 12px;
    padding: 12px;
    border-radius: 10px;
    background: #222a33;
    box-shadow: 0 2px 8px #0002;
  }
  .mobile-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .host-action-btns {
    flex-direction: column;
    align-items: flex-end;
    align-self: flex-end;
    margin-right: 4px;
    gap: 8px;
  }
  .host-action-btns .v-btn {
    width: 72px;
    min-width: 0;
    justify-content: center;
    margin-right: 0 !important;
    margin-bottom: 4px;
  }
}
/* .close-btn 样式已集成到内联style，可保留空或加hover效果 */
 .close-btn:hover {
   background: #7c3aed !important;
   box-shadow: 0 4px 16px #a259f7cc;
 }
.glow-btn-blue {
  background: linear-gradient(90deg, #2196f3 0%, #3f51b5 100%) !important;
}
.glow-btn-cyan {
  background: linear-gradient(90deg, #00eaff 0%, #00bcd4 100%) !important;
}
.glow-btn-orange {
  background: linear-gradient(90deg, #ff9800 0%, #ff5722 100%) !important;
}
.glow-btn-purple {
  background: linear-gradient(90deg, #a259f7 0%, #e040fb 100%) !important;
}
.glow-btn-green {
  background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%) !important;
}
.glow-btn-pink {
  background: linear-gradient(90deg, #ff6a88 0%, #ff99ac 100%) !important;
}
.glow-btn-multicolor {
  background: linear-gradient(90deg, #ff6a88 0%, #ffd600 30%, #43e97b 60%, #00eaff 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 16px 0 #ffd60088, 0 2px 16px 0 #00eaff55;
  border: none;
}
.glow-btn-multicolor:hover {
  box-shadow: 0 4px 32px 0 #ff6a88cc, 0 4px 32px 0 #00eaffcc;
  background: linear-gradient(90deg, #00eaff 0%, #43e97b 30%, #ffd600 60%, #ff6a88 100%) !important;
}
.glow-btn-rainbow {
  background: linear-gradient(90deg, #ff6a88 0%, #ffd600 20%, #43e97b 40%, #38f9d7 60%, #00eaff 80%, #a259f7 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 16px 0 #ffd60088, 0 2px 16px 0 #00eaff55;
  border: none;
}
.glow-btn-rainbow:hover {
  box-shadow: 0 4px 32px 0 #ff6a88cc, 0 4px 32px 0 #00eaffcc;
  background: linear-gradient(90deg, #a259f7 0%, #00eaff 20%, #38f9d7 40%, #43e97b 60%, #ffd600 80%, #ff6a88 100%) !important;
}

.glow-btn-gold {
  background: linear-gradient(90deg, #ffd700 0%, #ffb300 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 16px 0 #ffd70088, 0 2px 16px 0 #ffb30055;
  border: none;
}
.glow-btn-gold:hover {
  box-shadow: 0 4px 32px 0 #ffd700cc, 0 4px 32px 0 #ffb300cc;
  background: linear-gradient(90deg, #ffb300 0%, #ffd700 100%) !important;
}
</style>

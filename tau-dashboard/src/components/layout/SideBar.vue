<template>
  <div class="layout-side-bar">
    <div class="layout-side-bar-header">
      <img class="logo" src="../../assets/img/logo-light.png" />
      <span class="name"
        ><strong>T</strong>witch <strong>A</strong>PI
        <strong>U</strong>nifier</span
      >
      <br />
      <p>{{ username }}</p>
    </div>
    <ul class="layout-side-bar-menu">
      <li v-for="item in items" :key="item.label">
        <router-link :to="item.routeTo">
          <i class="pi" :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
export default defineComponent({
  name: 'SideBar',
  setup(props, context) {
    const store = useStore();
    const router = useRouter();
    const username = ref(localStorage.getItem('tau-username'));
    const items = ref([
      {
        label: 'Dashboard',
        icon: 'pi pi-desktop',
        routeTo: '/dashboard',
      },
      {
        label: 'Streamers',
        icon: 'pi pi-video',
        routeTo: '/dashboard/streamers',
      },
      {
        label: 'Config',
        icon: 'pi pi-cog',
        routeTo: '/dashboard/config',
      },
      {
        label: 'User',
        icon: 'pi pi-user',
        routeTo: '/dashboard/user',
      },
      {
        label: 'Webhooks',
        icon: 'pi pi-sitemap',
        routeTo: '/dashboard/webhook-monitor',
      },
    ]);
    return {
      items,
      username,
    };
  },
});
</script>

<style lang="scss">
.layout-side-bar {
  position: fixed;
  width: 250px;
  height: 100%;
  z-index: 999;
  overflow-y: auto;
  background-image: linear-gradient(#2f4050, #293846);
  .layout-side-bar-header {
    background-color: none;
    border-bottom: 1px solid var(--bluegray-600);
    color: #ffffff;
    span.name {
      vertical-align: middle;
      font-size: 18px;
    }
    .logo {
      vertical-align: middle;

      width: 31px;
      height: 31px;
      margin: 5px 10px;
      opacity: 40%;
      vertical-align: middle;
    }
  }
}

.layout-side-bar-menu {
  list-style-type: none;
  margin: 0;
  padding: 0;

  li {
    a {
      padding: 1em;
      border-bottom: 1px solid rgba(255, 255, 255, 0.15);
      font-size: 15px;
      color: #719ac2;
      cursor: pointer;
      text-decoration: none;
      position: relative;
      display: flex;
      align-items: center;

      i {
        font-size: 15px;
      }

      span {
        margin-left: 0.6em;
      }
      &.router-link-exact-active {
        color: #ffffff;
      }
    }
  }
}
</style>

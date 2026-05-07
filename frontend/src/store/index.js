import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: {
      username: localStorage.getItem('username') || '',
      token: localStorage.getItem('token') || '',
      isAdmin: localStorage.getItem('isAdmin') === 'true'
    },
    chatHistories: JSON.parse(localStorage.getItem('chatHistories')) || [],
    currentChat: null
  },
  mutations: {
    LOGIN(state, userData) {
      state.user.username = userData.username
      state.user.token = userData.token
      state.user.isAdmin = !!userData.isAdmin
      localStorage.setItem('username', userData.username)
      localStorage.setItem('token', userData.token)
      localStorage.setItem('isAdmin', userData.isAdmin ? 'true' : 'false')
    },
    LOGOUT(state) {
      state.user.username = ''
      state.user.token = ''
      state.user.isAdmin = false
      state.currentChat = null
      localStorage.removeItem('username')
      localStorage.removeItem('token')
      localStorage.removeItem('isAdmin')
    },
    ADD_CHAT_HISTORY(state, chatData) {
      const existingIndex = state.chatHistories.findIndex(chat => chat.id === chatData.id)
      if (existingIndex !== -1) {
        state.chatHistories[existingIndex] = chatData
      } else {
        state.chatHistories.unshift(chatData)
      }
      localStorage.setItem('chatHistories', JSON.stringify(state.chatHistories))
    },
    UPDATE_CHAT_HISTORY(state, { chatId, messages }) {
      const chat = state.chatHistories.find(chat => chat.id === chatId)
      if (chat) {
        chat.messages = messages
        chat.updatedAt = new Date().toISOString()
        localStorage.setItem('chatHistories', JSON.stringify(state.chatHistories))
      }
    },
    SET_CURRENT_CHAT(state, chat) {
      state.currentChat = chat
    },
    DELETE_CHAT_HISTORY(state, chatId) {
      state.chatHistories = state.chatHistories.filter(chat => chat.id !== chatId)
      localStorage.setItem('chatHistories', JSON.stringify(state.chatHistories))
    }
  },
  actions: {
    login({ commit }, userData) {
      commit('LOGIN', userData)
    },
    logout({ commit }) {
      commit('LOGOUT')
    },
    saveChatHistory({ commit }, chatData) {
      commit('ADD_CHAT_HISTORY', chatData)
    },
    updateChatHistory({ commit }, payload) {
      commit('UPDATE_CHAT_HISTORY', payload)
    },
    setCurrentChat({ commit }, chat) {
      commit('SET_CURRENT_CHAT', chat)
    },
    deleteChatHistory({ commit }, chatId) {
      commit('DELETE_CHAT_HISTORY', chatId)
    }
  },
  getters: {
    isLoggedIn: state => !!state.user.token,
    username: state => state.user.username,
    isAdmin: state => state.user.isAdmin,
    chatHistories: state => state.chatHistories,
    currentChat: state => state.currentChat,
    getChatHistoriesByCourse: (state) => (courseId) => {
      return state.chatHistories.filter(chat => chat.courseId === courseId)
    }
  }
})
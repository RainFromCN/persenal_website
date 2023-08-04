import axios from 'axios'


export const circleUrl = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";


export const headerData = {
    // 与注册相关
    signup: {
        visible: false,
        username: '',
        password: '',
        confirm: '',
    },

    // 与登录相关
    login: {
        visible: '',
        login_username: '',
        login_password: '',
    },

    request: {
        visible: false,
        field: '',
        type: '',
        title: '',
        detail: '',
        rules: {
            field: [
                { required: true, message: '请选择所属的领域', trigger: 'change' },
            ],
            type: [
                { required: true, message: '请选择活动区域', trigger: 'blur' },
            ],
            title: [
                { required: true, message: '请输入需求的标题', trigger: 'blur' },
                { min: 8, max: 20, message: '长度在 8 到 20 个字符之间', trigger: 'blur' },
            ],
            detail: [
                { required: true, message: '请输入详细需求', trigger: 'blur' },
            ],
        },
    },

    user: {
        edit_visible: false,
        browse_req_visible: false,
        browse_bid_visible: false,
        tel: '',
        introduction: '',
        rules: {
            tel: [
                { required: true, message: '请输入手机号码', trigger: 'blur' },
                { min: 11, max: 11, message: '长度为 11 位', trigger: 'change' },
            ],
            introduction: [
                { required: true, message: '请输入个人简介', trigger: 'blur' },
                { min: 20, max: 100, message: '长度在 20 到 100 个字符之间', trigger: 'change' },
            ],
        }
    },
};


export const headerAPI = {
    signupSubmit: function() {
        const data = {
            signup_username: this.headerData.signup.username,
            signup_password: this.headerData.signup.password,
            signup_confirm: this.headerData.signup.confirm,
        }
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        axios.post('/help/signup/', data, { headers })
        .then(response => {
            // 处理返回后台的数据
            if (response.data.message) {
                this.$message.error(response.data.message)
            }
            else if (response.data.success) {
                this.$message.success('注册成功')
                this.headerData.signup.visible = false;
                location.reload()
            }
        })
    },

    loginSubmit: function() {
        const data = {
            login_username: this.headerData.login.username,
            login_password: this.headerData.login.password,
        }
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        axios.post('/help/login/', data, { headers })
        .then(response => {
            if (response.data.message) {
                this.$message.error(response.data.message)
            }
            else if (response.data.success) {
                this.headerData.login.visible = false;
                location.reload()
            }
        })
    },

    exitSubmit: function() {
        const data = {}
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        axios.post('/help/exit/', data, { headers })
        .then(response => {
            location.reload()
        })
    },

    requestSubmit: function() {
        const data = {
            field: this.headerData.request.field,
            type: this.headerData.request.type,
            title: this.headerData.request.title,
            detail: this.headerData.request.detail,
        }
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        this.$refs['ruleForm'].validate((valid) => {
            if (valid) {
                axios.post('/help/request_publish/', data, { headers })
                .then(response => {
                    if (response.data.message) {
                        this.$message.error(response.data.message)
                    }
                    else if (response.data.success) {
                        this.$message({
                            message: '发布成功，请在个人页面进行查看',
                            type: 'success',
                        })
                        this.headerData.request.visible = false;
                    }
                })
            }
        })
    },

    editSubmit: function() {
        const data = {
            tel: this.headerData.user.tel,
            introduction: this.headerData.user.introduction,
        }
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        this.$refs['editForm'].validate((valid) => {
            if (valid) {
                axios.post('/help/edit_information/', data, { headers })
                .then(response => {
                    if (response.data.message) {
                        this.$message.error(response.data.message)
                    }
                    else if (response.data.success) {
                        this.$message({
                            message: '个人资料修改成功',
                            type: 'success',
                        })
                        this.headerData.user.edit_visible = false;
                    }
                })
            }
        })
    },
};
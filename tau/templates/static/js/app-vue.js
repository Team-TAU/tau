var rewardSelect = new Vue({
  el:'#reward',
  delimiters:["[[","]]"],
  data:{
    alwaysOptions:[
      {id:"575c2991-cbc2-402c-837f-86bd40009379", label:"Test"}
    ],
    fetchedOptions:[]
  }
});
var rewardErrorMsg = new Vue({
  el:'#reward-error',
  delimiters:["[[", "]]"],
  data:{
    error:""
  }
});

<%@ page pageEncoding="utf-8"%>
<script>
function gotoPage(pagenum){
  document.PageForm.pageNo.value = pagenum;
  document.PageForm.submit();
  return ;
}
</script>

<span style="position: relative; left: -45px;">每页<%=pageBean.rowsPerPage%>行
</span>
<span style="position: relative; left: -25px;">共<%=pageBean.maxRowCount%>行
</span>
<span style="position: relative; left: 20px;">第<%=pageBean.curPage%>页
</span>
<span style="position: relative; left: 45px;">共<%=pageBean.maxPage%>页
</span>

<br />
<%
   if(pageBean.curPage==1){ 
        out.print(" <span style=\"position: relative ;left:-30px;\">首页 </span><span style=\"position: relative ;left:-20px;\"> 上一页</span>");
   }else{  
 %>
<span style="position: relative; left: -30px;"><a
	href="javascript:gotoPage(1)">首页</a></span>
<span style="position: relative; left: -20px;"><a
	href="javascript:gotoPage(<%=pageBean.curPage-1%>)">上一页</a></span>
<%}%>
<%
   if(pageBean.curPage==pageBean.maxPage){ 
        out.print("<span style=\"position: relative ;left:-10px;\">下一页 </span><span style=\"position: relative ;left:0px;\">尾页 </span>");
   }else{  
 %>
<span style="position: relative; left: -10px;"><a
	href="javascript:gotoPage(<%=pageBean.curPage+1%>)">下一页</A></span>
<span style="position: relative; left: 0px;"><a
	href="javascript:gotoPage(<%=pageBean.maxPage%>)">尾页</A></span>
<%}%>
<span style="position: relative; left: 20px;">转到第<input
	type="text" name="pageNo" style="width: 50px;" />页
</span>
<span style="position: relative; left: 30px;"><input
	type="submit" value="提交"></span>


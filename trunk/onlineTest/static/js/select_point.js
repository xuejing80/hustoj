 jQuery(document).ready(function () {
            $("[name='classname']").change(function () {
                $("[name='knowledgePoint2']").empty();
                $("[name='knowledgePoint2']").append("<option value=\"0\">全部二级知识点</option>");
                $("[name='knowledgePoint1']").empty();
                $("[name='knowledgePoint1']").append("<option value=\"0\">全部一级知识点</option>");
                $.ajax({
                    type: "post",
                    url: "{% url 'select_point' %}",
                    dataType: "json",
                    data: {'course': $(this).val(), 'parent': 0},
                    success: function (data) {
                        for (var p in data) {
                            $("[name='knowledgePoint1']").append("<option value=\"" + p + "\">" + data [p] + "</option>");
                        }
                    }
                });
            });
            $("[name='knowledgePoint1']").change(function () {
                $("[name='knowledgePoint2']").empty();
                $("[name='knowledgePoint2']").append("<option value=\"0\">全部二级知识点</option>");
                $.ajax({
                    type: "post",
                    url: "{% url 'select_point' %}",
                    dataType: "json",
                    data: {'parent': $(this).val()},
                    success: function (data) {
                        for (var p in data) {
                            $("[name='knowledgePoint2']").append("<option value=\"" + p + "\">" + data [p] + "</option>");
                        }
                    }
                });
            });
        })/**
 * Created by gaoliang on 16-7-26.
 */
